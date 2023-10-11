# -*- coding: utf-8 -*-
import io
import xlsxwriter
from odoo import models, fields, api
import base64

class ReportFacturasVencidas(models.TransientModel):
    _name = 'report.facturas.vencidas'
    _description = 'Reporte de Facturas Vencidas'

    name = fields.Char(string='Nombre Archivo', default="Facturas Vencidas.xlsx")
    report_data = fields.Binary(string='Reporte',)
    fecha = fields.Date(string="Fecha",default=fields.Date.today())

    @api.model
    def _get_facturas_vencidas(self):
        # Obtener las facturas vencidas por cobrar
        facturas = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('amount_residual', '>', 0.0),
            ('invoice_date_due', '<', self.fecha)
        ], order="partner_id ASC")
        facturas_por_vencer = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('amount_residual', '>', 0.0),
            ('invoice_date_due', '>', self.fecha)
        ], order="partner_id ASC")
        facturas_del_dia = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '=', self.fecha)
        ], order="partner_id ASC")
        pagos_del_dia = self.env['account.payment'].search([
            ('state', '=', 'posted'),
            ('date', '=', self.fecha)
        ], order="partner_id ASC")

        facturas_dict = {}
        facturas_por_cliente = {}

        total_por_cobrar = 0.0
        total_facturado_dia = 0.0
        total_pendiente_cobrar = 0.0
        total_pendiente_vencer = 0.0
        total_vencidas_1_15_dias = 0.0
        total_vencidas_16_mas_dias = 0.0
        total_procesado_dia = 0

        for factura in facturas:
            partner_id = factura.partner_id.id
            vendedor = factura.user_id.name if factura.user_id else ''
            dias_vencimiento = (fields.Date.today() - factura.invoice_date_due).days

            if partner_id not in facturas_por_cliente:
                facturas_por_cliente[partner_id] = []

            facturas_por_cliente[partner_id].append(factura)

            #total_por_cobrar += factura.amount_residual if factura.currency_id == self.env.company.currency_id else factura.amount_residual_signed_ref

            #if factura.invoice_date_due == fields.Date.today():
                #total_facturado_dia += factura.amount_residual if factura.currency_id == self.env.company.currency_id else factura.amount_residual_signed_ref

            #if dias_vencimiento > 0:
            #    if dias_vencimiento <= 15:
            #        total_vencidas_1_15_dias += factura.amount_residual if factura.currency_id == self.env.company.currency_id else factura.amount_residual_signed_ref
            #    else:
            #        total_vencidas_16_mas_dias += factura.amount_residual if factura.currency_id == self.env.company.currency_id else factura.amount_residual_signed_ref
        for partner_id, facturas_cliente in facturas_por_cliente.items():
            por_cobrar = sum(factura.amount_residual for factura in facturas_cliente if factura.partner_id.id == partner_id and factura.currency_id == self.env.company.currency_id) + sum(factura.amount_residual_signed_ref for factura in facturas_cliente if factura.partner_id.id == partner_id and factura.currency_id != self.env.company.currency_id)
            facturado_del_dia = sum(facturas_del_dia.filtered(lambda x: x.partner_id.id == partner_id and x.currency_id == self.env.company.currency_id).mapped('amount_total')) + sum(facturas_del_dia.filtered(lambda x: x.partner_id.id == partner_id and x.currency_id != self.env.company.currency_id).mapped('amount_ref'))
            procesado_dia = sum(pagos_del_dia.filtered(lambda x: x.partner_id.id == partner_id and x.currency_id == self.env.company.currency_id).mapped('amount_total')) + sum(pagos_del_dia.filtered(lambda x: x.partner_id.id == partner_id and x.currency_id != self.env.company.currency_id).mapped('amount_ref'))
            pendientes_por_vencer = sum(facturas_por_vencer.filtered(lambda x: x.partner_id.id == partner_id and x.currency_id == self.env.company.currency_id).mapped('amount_residual')) + sum(facturas_por_vencer.filtered(lambda x: x.partner_id.id == partner_id and x.currency_id != self.env.company.currency_id).mapped('amount_residual_signed_ref'))
            total_procesado_dia += procesado_dia
            total_facturado_dia += facturado_del_dia
            total_por_cobrar += por_cobrar
            total_pendiente_cobrar += (por_cobrar + facturado_del_dia - procesado_dia)
            total_pendiente_vencer += pendientes_por_vencer
            total_vencidas_1_15_dias += sum(factura.amount_residual for factura in facturas_cliente if factura.partner_id.id == partner_id and 0 < (fields.Date.today() - factura.invoice_date_due).days <= 15 and factura.currency_id == self.env.company.currency_id) + sum(factura.amount_residual_signed_ref for factura in facturas_cliente if factura.partner_id.id == partner_id and 0 < (fields.Date.today() - factura.invoice_date_due).days <= 15 and factura.currency_id != self.env.company.currency_id)
            total_vencidas_16_mas_dias += sum(factura.amount_residual for factura in facturas_cliente if factura.partner_id.id == partner_id and (fields.Date.today() - factura.invoice_date_due).days > 15 and factura.currency_id == self.env.company.currency_id) + sum(factura.amount_residual for factura in facturas_cliente if factura.partner_id.id == partner_id and (fields.Date.today() - factura.invoice_date_due).days > 15 and factura.currency_id != self.env.company.currency_id)
            facturas_dict[partner_id] = {
                'POSICION': 0,
                'VENDEDOR': facturas_cliente[0].user_id.name if facturas_cliente[0].user_id else '',
                'POR COBRAR': por_cobrar,
                'FACTURADO EN EL DIA': facturado_del_dia,
                'PROCESADO EN EL DIA': procesado_dia,
                'PENDIENTE POR COBRAR': por_cobrar + facturado_del_dia - procesado_dia,
                'PENDIENTE POR VENCER': pendientes_por_vencer,
                'VENCIDAS DE 1-15 DIAS': sum(factura.amount_residual for factura in facturas_cliente if 0 < (fields.Date.today() - factura.invoice_date_due).days <= 15 and factura.currency_id == self.env.company.currency_id) + sum(factura.amount_residual_signed_ref for factura in facturas_cliente if 0 < (fields.Date.today() - factura.invoice_date_due).days <= 15 and factura.currency_id != self.env.company.currency_id),
                'VENCIDAS DE 16 A MAS DIAS': sum(factura.amount_residual for factura in facturas_cliente if (fields.Date.today() - factura.invoice_date_due).days > 15 and factura.currency_id == self.env.company.currency_id) + sum(factura.amount_residual for factura in facturas_cliente if (fields.Date.today() - factura.invoice_date_due).days > 15 and factura.currency_id != self.env.company.currency_id),
            }

        #total_pendiente_cobrar = total_por_cobrar - total_facturado_dia
        #total_pendiente_vencer = total_pendiente_vencer - total_vencidas_1_15_dias - total_vencidas_16_mas_dias

        return facturas_dict, total_por_cobrar, total_facturado_dia, total_pendiente_cobrar, total_pendiente_vencer, total_vencidas_1_15_dias, total_vencidas_16_mas_dias,total_procesado_dia

    def generate_report(self):
        # Obtener las facturas vencidas
        facturas_dict, total_por_cobrar, total_facturado_dia, total_pendiente_cobrar, total_pendiente_vencer, total_vencidas_1_15_dias, total_vencidas_16_mas_dias,total_procesado_dia = self._get_facturas_vencidas()

        # Crear el archivo Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Facturas Vencidas')

        # Establecer el formato para el encabezado centrado
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})

        # Establecer el formato numérico para las columnas con valores numéricos
        numeric_format = workbook.add_format({'num_format': '#,##0.00'})

        # Escribir el encabezado centrado en 3 filas y 6 columnas
        worksheet.merge_range(0, 0, 2, 5, 'RESUMEN GLOBAL DE COBRANZA', header_format)

        # Establecer los encabezados
        headers = ['POSICION', 'VENDEDOR', 'CLIENTE', 'POR COBRAR', 'FACTURADO EN EL DIA', 'PROCESADO EN EL DIA',
           'PENDIENTE POR COBRAR', 'PENDIENTE POR VENCER', 'VENCIDAS DE 1-15 DIAS', 'VENCIDAS DE 16 A MAS DIAS']
        col = 0
        for header in headers:
            worksheet.write(3, col, header, header_format)
            col += 1

        # Escribir los datos de las facturas
        row = 4
        cont = 1
        for partner_id, data in facturas_dict.items():
            worksheet.write(row, 0, cont)
            worksheet.write(row, 1, data['VENDEDOR'])
            cliente = self.env['res.partner'].browse(partner_id).name
            worksheet.write(row, 2, cliente)
            worksheet.write(row, 3, data['POR COBRAR'], numeric_format)
            worksheet.write(row, 4, data['FACTURADO EN EL DIA'], numeric_format)
            worksheet.write(row, 5, data['PROCESADO EN EL DIA'], numeric_format)
            worksheet.write(row, 6, data['PENDIENTE POR COBRAR'], numeric_format)
            worksheet.write(row, 7, data['PENDIENTE POR VENCER'], numeric_format)
            worksheet.write(row, 8, data['VENCIDAS DE 1-15 DIAS'], numeric_format)
            worksheet.write(row, 9, data['VENCIDAS DE 16 A MAS DIAS'], numeric_format)
            row += 1
            cont += 1

        # Escribir los totales
        worksheet.write(row, 1, 'Total', header_format)
        worksheet.write(row, 3, total_por_cobrar, numeric_format)
        worksheet.write(row, 4, total_facturado_dia, numeric_format)
        worksheet.write(row, 5, total_procesado_dia, numeric_format)
        worksheet.write(row, 6, total_pendiente_cobrar, numeric_format)
        worksheet.write(row, 7, total_pendiente_vencer, numeric_format)
        worksheet.write(row, 8, total_vencidas_1_15_dias, numeric_format)
        worksheet.write(row, 9, total_vencidas_16_mas_dias, numeric_format)

        workbook.close()
        output.seek(0)

        # Guardar el archivo Excel en un campo binario
        self.write({'report_data': base64.b64encode(output.getvalue())})

        # Hacer algo con el archivo generado, como descargarlo o enviarlo por correo electrónico
        return {
            'name': 'Facturas Vencidas',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }
    
    
