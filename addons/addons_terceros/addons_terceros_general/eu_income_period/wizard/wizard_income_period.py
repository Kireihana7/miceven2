# -*- coding: utf-8 -*-
#################################################################################
# Author      : CorpoEureka
# Copyright(c): 2021-Present CorpoEureka.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import xlsxwriter
import base64
from io import BytesIO


class WizardReportIncomePeriod(models.TransientModel):
    _name = 'wizard.report.income.period'
    _description = "Ingresos del Período"

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.user.company_id.id)
    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    ######
    states = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    name = fields.Char(string='Nombre del Archivo', readonly=True)
    data = fields.Binary(string='Archivo', readonly=True)

    @api.model
    def default_get(self, default_fields):
        vals = super(WizardReportIncomePeriod, self).default_get(default_fields)
        vals['states'] = 'choose'
        return vals

    def go_back(self):
        self.states = 'choose'
        return {
            'name': 'Ingresos del Periodo',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }



    def print_xls_report(self):
        domain = []
        if self.date_start:
            domain.append(('date','>=',self.date_start))
        if self.date_end:
            domain.append(('date','<=',self.date_end))
        domain.append(('company_id','=',self.env.company.id))
        pagos = self.env['account.payment'].search(domain,order="date ASC")
        #raise UserError(pagos)

        xls_filename = 'ingresos_del_periodo.xlsx'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        #report_stock_inv_obj = self.env['report.eu_income_period.report_income_period']

        header_merge_format = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':10, 'bg_color':'#D3D3D3', 'border':1})

        header_merge_format_titulo = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':16, 'bg_color':'#D3D3D3', 'border':1})

        header_data_format = workbook.add_format({'align':'center', 'valign':'vcenter', \
                                                   'font_size':10, 'border':1})

        header_data_format_titulo = workbook.add_format({'align':'center', 'valign':'vcenter', \
                                                   'font_size':12, 'border':1})

        product_header_format = workbook.add_format({'valign':'vcenter', 'font_size':10, 'border':0})
        product_header_format_2 = workbook.add_format({'valign':'vcenter', 'font_size':10, 'border':1})

        currency_format = workbook.add_format({'num_format': '#,##0.00', 'font_size':10, 'border':1})
        fecha = workbook.add_format({'num_format': 'dd/mm/YYYY', 'border':1})

        worksheet = workbook.add_worksheet('Ingresos del periodo')
        worksheet.merge_range(0, 0, 1, 3, self.company_id.name, header_data_format_titulo)
        worksheet.write(0,6, 'Fecha:', product_header_format)
        worksheet.write_datetime(0,7, datetime.now(), fecha)

        worksheet.set_column('A:B', 18)
        worksheet.set_column('C:I', 12)

        worksheet.merge_range(4, 2, 5, 10,  'Ingresos para el Período', header_merge_format_titulo)

        worksheet.merge_range(7, 0, 7, 9,  'Información del Pago', header_merge_format)

        worksheet.write(8, 0, "Fecha", header_merge_format)
        worksheet.write(8, 1, "Grupo", header_merge_format)
        worksheet.write(8, 2, "Número", header_merge_format)
        worksheet.write(8, 3, "Circular", header_merge_format)

        worksheet.write(8, 4, "Doc-Fecha", header_merge_format)
        worksheet.write(8, 5, "Doc-Cliente", header_merge_format)
        worksheet.write(8, 6, "Doc-No", header_merge_format)
        worksheet.write(8, 7, "Doc-Vend", header_merge_format)
        worksheet.write(8, 8, "Doc-Monto", header_merge_format)
        worksheet.write(8, 9, "Pagado", header_merge_format)
        
        row = 8

        fechas = []
        diarios_id = []
        for fe in pagos:
            if fe.date not in fechas:
                fechas.append(fe.date)

            if fe.journal_id.id not in diarios_id:
                diarios_id.append(fe.journal_id.id)

        diarios_obj = self.env['account.journal'].search([('company_id','=',self.env.company.id),('id','in',(diarios_id))])
        
        col_1 = 10
        col_2 = 11
        diarios_n = len(diarios_obj.filtered(lambda x: x.currency_id == self.env.company.currency_id or not x.currency_id))
        diarios_e = len(diarios_obj.filtered(lambda x: x.currency_id != self.env.company.currency_id and x.currency_id))

        name_cols = []

        if diarios_n == 1:
            worksheet.write(7, col_1, 'Nacionales', header_merge_format)
        else:
            worksheet.merge_range(7, col_1, 7, col_1+diarios_n-1, 'Nacionales', header_merge_format)
        
        if diarios_e == 1 and diarios_n == 1:
            worksheet.write(7, col_2, 'Divisas', header_merge_format)
        elif diarios_e == 1 and diarios_n > 1:
            worksheet.write(7, col_1+diarios_n, 'Divisas', header_merge_format)
        else:
            worksheet.merge_range(7, col_1+diarios_n, 7, col_1+diarios_n+diarios_e-1,  'Divisas', header_merge_format)
        
        for diario in diarios_obj.filtered(lambda x: x.currency_id == self.env.company.currency_id or not x.currency_id):
            worksheet.write(8, col_1, diario.name, header_merge_format)
            name_cols.append(diario.name)
            col_1 += 1
        for diario in diarios_obj.filtered(lambda x: x.currency_id != self.env.company.currency_id and x.currency_id):
            worksheet.write(8, col_1, diario.name, header_merge_format)
            name_cols.append(diario.name)
            col_1 += 1

        for por_fecha in fechas:
            total_cobros = 0.00
            total_ventas = 0.00
            total_abonos = 0.00
            for pago in pagos.filtered(lambda x: (x.reconciled_invoices_count != 0 or x.reconciled_bills_count != 0) and x.partner_type == 'supplier' and x.payment_type == 'inbound').sorted(lambda m: (m.date)):
                #COBROS
                grupo = 'Abonos' if pago.reconciled_invoices_count == 0 and pago.reconciled_bills_count == 0 else 'Cobros' if pago.partner_type =='supplier' else 'Ventas'
                if pago.date == por_fecha:
                    row += 1
                    worksheet.write_datetime(row, 0, pago.date, fecha)
                    worksheet.write(row, 1, grupo, header_data_format)
                    worksheet.write(row, 2, pago.name, header_data_format)
                    worksheet.write(row, 3, pago.ref, header_data_format)
                    
                    worksheet.write_datetime(row, 4, pago.move_id.date if pago.move_id.date else '', fecha)
                    worksheet.write(row, 5, pago.move_id.partner_id.name if pago.move_id.partner_id.name else '', header_data_format)
                    worksheet.write(row, 6, pago.move_id.name if pago.move_id.name else '', header_data_format)
                    worksheet.write(row, 7, pago.move_id.invoice_user_id.name if pago.move_id.invoice_user_id.name else '', header_data_format)
                    worksheet.write(row, 8, pago.move_id.amount_total if pago.move_id.amount_total else '', currency_format)
                    worksheet.write(row, 9, pago.amount, currency_format)
                    colum = 9
                    for nc in name_cols:
                        colum += 1
                        worksheet.write(row, colum, pago.amount if nc==pago.move_id.journal_id.name else 0.00, currency_format)

                    total_cobros += pago.amount
            if len(pagos.filtered(lambda x: (x.reconciled_invoices_count != 0 or x.reconciled_bills_count != 0) and x.partner_type == 'supplier' and x.date == por_fecha ))>0: 
                row += 1
                #Subtotales
                worksheet.merge_range(row, 7, row, 8,  'Sub-Total '+grupo, header_merge_format)
                worksheet.write(row, 9, total_cobros, currency_format)
                colum = 9
                for nc in name_cols:
                    colum += 1
                    acum_valor_1 = sum(pagos.filtered(lambda x: x.move_id.journal_id.name == nc and x.date == por_fecha and (x.reconciled_invoices_count != 0 or x.reconciled_bills_count != 0) and x.partner_type == 'supplier' and x.payment_type == 'inbound').mapped('amount'))
                    worksheet.write(row, colum, acum_valor_1, currency_format)
                row += 1

            for pago in pagos.filtered(lambda x: x.reconciled_invoices_count == 0 and x.reconciled_bills_count == 0 and x.payment_type == 'inbound').sorted(lambda m: (m.date)):
                #ABONOS
                grupo = 'Abonos' if pago.reconciled_invoices_count == 0 and pago.reconciled_bills_count == 0 else 'Cobros' if pago.partner_type =='supplier' else 'Ventas'
                if pago.date == por_fecha:
                    row += 1
                    worksheet.write_datetime(row, 0, pago.date, fecha)
                    worksheet.write(row, 1, grupo, header_data_format)
                    worksheet.write(row, 2, pago.name, header_data_format)
                    worksheet.write(row, 3, pago.ref, header_data_format)
                    
                    worksheet.write_datetime(row, 4, pago.move_id.date if pago.move_id.date else '', fecha)
                    worksheet.write(row, 5, pago.move_id.partner_id.name if pago.move_id.partner_id.name else '', header_data_format)
                    worksheet.write(row, 6, pago.move_id.name if pago.move_id.name else '', header_data_format)
                    worksheet.write(row, 7, pago.move_id.invoice_user_id.name if pago.move_id.invoice_user_id.name else '', header_data_format)
                    worksheet.write(row, 8, pago.move_id.amount_total if pago.move_id.amount_total else '', currency_format)
                    worksheet.write(row, 9, pago.amount, currency_format)

                    colum = 9
                    for nc in name_cols:
                        colum += 1
                        worksheet.write(row, colum, pago.amount if nc==pago.move_id.journal_id.name else 0.00, currency_format)

                    total_abonos += pago.amount
            if len(pagos.filtered(lambda x: x.reconciled_invoices_count == 0 and x.reconciled_bills_count == 0 and x.date == por_fecha))>0:
                row += 1
                #Subtotales
                worksheet.merge_range(row, 7, row, 8,  'Sub-Total '+grupo, header_merge_format)
                worksheet.write(row, 9, total_abonos, currency_format)
                colum = 9
                for nc in name_cols:
                    colum += 1
                    acum_valor_1 = sum(pagos.filtered(lambda x: x.move_id.journal_id.name == nc and x.date == por_fecha and x.reconciled_invoices_count == 0 and x.reconciled_bills_count == 0 and x.payment_type == 'inbound').mapped('amount'))
                    worksheet.write(row, colum, acum_valor_1, currency_format)
                row += 1

            for pago in pagos.filtered(lambda x: (x.reconciled_invoices_count != 0 or x.reconciled_bills_count != 0) and x.partner_type != 'supplier' and x.payment_type == 'inbound').sorted(lambda m: (m.date)):
                #VENTAS
                grupo = 'Abonos' if pago.reconciled_invoices_count == 0 and pago.reconciled_bills_count == 0 else 'Cobros' if pago.partner_type =='supplier' else 'Ventas'
                if pago.date == por_fecha:
                    row += 1
                    worksheet.write_datetime(row, 0, pago.date, fecha)
                    worksheet.write(row, 1, grupo, header_data_format)
                    worksheet.write(row, 2, pago.name, header_data_format)
                    worksheet.write(row, 3, pago.ref, header_data_format)
                    
                    worksheet.write_datetime(row, 4, pago.move_id.date if pago.move_id.date else '', fecha)
                    worksheet.write(row, 5, pago.move_id.partner_id.name if pago.move_id.partner_id.name else '', header_data_format)
                    worksheet.write(row, 6, pago.move_id.name if pago.move_id.name else '', header_data_format)
                    worksheet.write(row, 7, pago.move_id.invoice_user_id.name if pago.move_id.invoice_user_id.name else '', header_data_format)
                    worksheet.write(row, 8, pago.move_id.amount_total if pago.move_id.amount_total else '', currency_format)
                    worksheet.write(row, 9, pago.amount, currency_format)
                    
                    colum = 9
                    for nc in name_cols:
                        colum += 1
                        worksheet.write(row, colum, pago.amount if nc==pago.move_id.journal_id.name else 0.00, currency_format)

                    total_ventas += pago.amount
            
            if len(pagos.filtered(lambda x: (x.reconciled_invoices_count != 0 or x.reconciled_bills_count != 0) and x.partner_type != 'supplier' and x.date == por_fecha))>0:
                row += 1
                #Subtotales
                worksheet.merge_range(row, 7, row, 8,  'Sub-Total '+grupo, header_merge_format)
                worksheet.write(row, 9, total_ventas, currency_format)
                colum = 9
                for nc in name_cols:
                    colum += 1
                    acum_valor_1 = sum(pagos.filtered(lambda x: x.move_id.journal_id.name == nc and x.date == por_fecha and (x.reconciled_invoices_count != 0 or x.reconciled_bills_count != 0) and x.partner_type != 'supplier' and x.payment_type == 'inbound').mapped('amount'))
                    worksheet.write(row, colum, acum_valor_1, currency_format)
                row += 1

            #Totales
            row += 1
            worksheet.merge_range(row, 6, row, 8,  'Total Ingresos del día..', header_merge_format)
            worksheet.write(row, 9, (total_cobros+total_ventas+total_abonos), currency_format)
            colum = 9
            for nc in name_cols:
                colum += 1
                acum_valor_1 = sum(pagos.filtered(lambda x: x.move_id.journal_id.name == nc and x.date == por_fecha  and x.payment_type == 'inbound').mapped('amount'))
                worksheet.write(row, colum, acum_valor_1, currency_format)
            row += 2
        
        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write({
            'states': 'get',
            'data': out,
            'name': xls_filename
        })
        return {
            'name': 'Reporte de Productos',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

