from odoo import models, fields, api
import io
import xlsxwriter
import base64
from odoo.exceptions import UserError

class EstadoCuentaCliente(models.TransientModel):
    _name = 'estado.cuenta.cliente'

    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    name = fields.Char(string='Nombre Archivo', default="Estado Cliente.xlsx")
    from_date = fields.Date(string="Desde")
    to_date = fields.Date(string="Hasta")
    sin_fecha = fields.Boolean(string="Sin Fecha")
    report_data = fields.Binary(string='Reporte')

    def generate_invoices(self):
        # Obtener todas las facturas de cliente publicadas
        domain = [('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('company_id', '=', self.env.company.id),
            ('partner_id', '=', self.partner_id.id)]
        if not self.sin_fecha:
            domain.append(('date', '>=', self.from_date))
            domain.append(('date', '<=', self.to_date))
        invoices = self.env['account.move'].search(domain)
        if not invoices:
            raise UserError('El cliente no tiene facturas')

        # Crear el archivo Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Facturas')

        # Formato numérico para los campos
        numeric_format = workbook.add_format({'num_format': '#,##0.00'})

        # Formato de fecha
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        # Establecer el formato para el encabezado centrado
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        # Escribir el encabezado centrado en 3 filas y 6 columnas
        worksheet.merge_range(0, 0, 2, 5, 'BALANCE DEL CLIENTE' + str(self.partner_id.name), header_format)
        # Escribir datos de las facturas y líneas en el archivo Excel
        row = 3
        col = 0
        headers = [
            'N° de Factura',
            'Fecha Prepago',
            'Total Unid. A Cargar',
            'Cant. por Kg.',
            'Precio Unid.',
            'Total Precio en $ / Unid.',
            'Precio por Total $',
            'Producto',
            'Unidad'
        ]
        # Escribir datos de las facturas y líneas en el archivo Excel
        for invoice in invoices:
            # Reiniciar la columna
            col = 0
            for header in headers:
                worksheet.write(row, col, header)
                col += 1
            # Escribir número de factura
            row += 1
            for line in invoice.invoice_line_ids:
                worksheet.write(row, 0, invoice.name)
                worksheet.write(row, 1, invoice.invoice_date.strftime('%d/%m/%Y'), date_format)
                worksheet.write(row, 2, line.quantity)
                worksheet.write(row, 3, line.product_id.weight * line.quantity)
                worksheet.write(row, 4, line.price_unit, numeric_format)
                worksheet.write(row, 5, line.price_subtotal, numeric_format)
                worksheet.write(row, 6, line.price_subtotal, numeric_format)
                worksheet.write(row, 7, line.product_id.name)
                worksheet.write(row, 8, line.product_uom_id.name if line.product_uom_id else 'N/A')
                row += 1

            # Obtener los pagos vinculados a la factura
            partials = invoice._get_reconciled_invoices_partials()

            if partials:
                # Salto de 3 filas para diferenciar los pagos
                row += 3
                col = 0
                # Escribir encabezado de pagos
                payment_headers = [
                    'Fecha Pago',
                    'Banco',
                    'Referencia',
                    'Tasa',
                    'Monto Pagado'
                ]
                for header in payment_headers:
                    worksheet.write(row, col, header)
                    col += 1
                row += 1
                col = 0
                # Escribir datos de pagos
                for partial, amount, invoice_line in partials:
                    payment_date = partial.credit_move_id.date.strftime('%d/%m/%Y')
                    payment_amount = amount
                    worksheet.write(row, col, payment_date, date_format)
                    worksheet.write(row, col + 1, partial.credit_move_id.journal_id.name if partial.credit_move_id.journal_id else 'N/A')
                    worksheet.write(row, col + 2 , partial.credit_move_id.ref if partial.credit_move_id else 'N/A')
                    worksheet.write(row, col + 3, partial.credit_move_id.manual_currency_exchange_rate if partial.credit_move_id else 0, numeric_format)
                    worksheet.write(row, col + 4, payment_amount, numeric_format)
                    row += 1

            # Calcular totales
            total_cargas = sum(line.price_subtotal for line in invoice.invoice_line_ids)
            total_cancelado = sum(amount for partial, amount, invoice_line in partials)
            monto_pendiente = total_cargas - total_cancelado

            # Escribir totales
            row+=1
            worksheet.write(row, 6 , 'Monto Total de Cargas') 
            worksheet.write(row, 7, total_cargas, numeric_format)  # Escribir el monto total de cargas
            row+=1
            worksheet.write(row, 6 , 'Monto Total de Cancelado') 
            worksheet.write(row, 7, total_cancelado, numeric_format)  # Escribir el monto total cancelado
            row+=1
            worksheet.write(row, 6 , 'Monto Pendiente por Cancelar') 
            worksheet.write(row, 7, monto_pendiente, numeric_format)  # Escribir el monto pendiente por cancelar

            # Reiniciar la columna para la siguiente factura
            col = 0
            row += 2

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, 8, 15)

        # Cerrar el archivo Excel
        workbook.close()
        output.seek(0)

        # Guardar el archivo Excel como un binary en el registro transitorio
        self.write({
            'report_data': base64.b64encode(output.getvalue()),
            'name': 'Estado Cliente ' + self.partner_id.name + '.xlsx'
        })

        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }


    def generate_invoices_pdf(self):
        # Obtener todas las facturas de cliente publicadas
        domain = [('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('company_id', '=', self.env.company.id),
            ('partner_id', '=', self.partner_id.id)]
        if not self.sin_fecha:
            domain.append(('date', '>=', self.from_date))
            domain.append(('date', '<=', self.to_date))
        invoicess = self.env['account.move'].search(domain)
        if not invoicess:
            raise UserError('El cliente no tiene facturas')
        invoices= []
        for invoice in invoicess:
            datas = []
            partialss= []
            partials = invoice._get_reconciled_invoices_partials()
            if partials:
                for partial, amount, invoice_line in partials:
                    payment_date = partial.credit_move_id.date.strftime('%d/%m/%Y')
                    payment_amount = amount
                    partialss.append({
                        'payment_date':payment_date,
                        'name':partial.credit_move_id.journal_id.name,
                        'ref':partial.credit_move_id.ref,
                        'manual_currency_exchange_rate':partial.credit_move_id.manual_currency_exchange_rate,
                        'payment_amount':payment_amount,
                    })
            invoices.append({
                'datas':datas,
                'partials':partialss,
            })
            for line in invoice.invoice_line_ids:
                datas.append({
                    'name':invoice.name,
                    'invoice_date':invoice.invoice_date.strftime("%d/%m/%Y"),
                    'quantity':line.quantity,
                    'weight':line.product_id.weight * line.quantity,
                    'price_unit':line.price_unit,
                    'price_subtotal':line.price_subtotal,
                    'price_subtotal':line.price_subtotal,
                    'product_id':line.product_id.name,
                    'product_uom_id':line.product_uom_id.name,
                    'total_cargas' : sum(line.price_subtotal for line in invoice.invoice_line_ids),
                    'total_cancelado' : sum(amount for partial, amount, invoice_line in partials),
                    'monto_pendiente' : sum(line.price_subtotal for line in invoice.invoice_line_ids) - sum(amount for partial, amount, invoice_line in partials),
                })

        res = {
            'from_date':   str(self.from_date.strftime("%d/%m/%Y")) if self.from_date else fields.Date.today(),
            'to_date':     str(self.to_date.strftime("%d/%m/%Y")) if self.to_date else fields.Date.today(),
            'sin_fecha':   True if self.sin_fecha else False,
            'company_name': self.env.company.name,
            'company_vat':  self.env.company.vat,
            'invoices':     invoices,
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_reporte_invoice_due.report_estado_cuenta_cliente').report_action([],data=data)