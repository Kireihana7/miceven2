# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import time
from datetime import timedelta, datetime, date

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError
import xlsxwriter
import base64
from io import BytesIO
import pytz
import datetime

class IslrXlsWizard(models.TransientModel):
    _name = 'islr.xls.wizard'

    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Proveedor o Cliente')
    move_type = fields.Selection([
        ('in_invoice', 'Cuentas Por Pagar'),
        ('out_invoice', 'Cuentas Por Cobrar'),
        ('in_refund', 'Notas de Credito'),
    ], string='Retenciones de ISLR', default='in_invoice', required=True,)

    state = fields.Selection([
        ('confirmed', 'Confirmado'),
        ('declared', 'Declarado'),
        ('done', 'Pagado'),
    ], string='Estatus de la retención')

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        string="Compañia",
        readonly=True,
    )

    name = fields.Char(string='Nombre del Archivo', readonly=True)
    data = fields.Binary(string='Archivo', readonly=True)
    states = fields.Selection([
        ('choose', 'choose'), 
        ('get', 'get')], 
        default='choose')

    @api.model
    def default_get(self, default_fields):
        vals = super(IslrXlsWizard, self).default_get(default_fields)
        vals['states'] = 'choose'
        return vals

    def go_back(self):
        self.states = 'choose'
        return {
            'name': 'ISLR Excel',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    def print_xls_report(self):
        final = []
        date_clause = ""
        query_params = []
        estatus_view = ''
        if self.company_id:
            date_clause += " AND awi.company_id = %s"
            query_params.append(self.company_id.id)
        if self.date_start:
            date_clause += " AND awi.date >= %s"
            query_params.append(self.date_start)
        if self.date_end:
            date_clause += " AND awi.date <= %s"
            query_params.append(self.date_end)
        if self.partner_id:
            date_clause += " AND awi.partner_id = %s"
            query_params.append(self.partner_id.id)
        if self.move_type:
            date_clause += " AND awi.move_type = %s"
            query_params.append(self.move_type)
        if self.state:
            date_clause += " AND awi.state = %s"
            query_params.append(self.state)
            if self.state == 'confirmed':
                estatus_view = 'Confirmado'
            elif self.state == 'declared':
                estatus_view = 'Declarado'
            elif self.state == 'done':
                estatus_view = 'Pagado'

        sql_islr = ("""
            SELECT awi.id, awi.date as fecha, awi.number as comprobante, awi.company_id, awi.partner_id, awi.move_type, 
            awil.descripcion||'-'||awil.code_withholding_islr as cod,
            awil.invoice_id, am.amount_total as monto_total, awil.base_tax as monto_base, awil.ret_amount as retenido, 
            awil.porc_islr as porcentaje_islr, awil.sustraendo as sustraendo, rp.name as proveedor, rp.residence_type as tipo_residencia, 
            rp.rif as rif, rc.name, 
            awrtl.apply_up_to, awrt.factor, awrt.parcentage_subtracting_1 as sus_1, awrt.parcentage_subtracting_3 as sus_3
            FROM account_wh_islr awi
            inner join account_wh_islr_line as awil on awil.withholding_id=awi.id
            inner join res_partner as rp on rp.id=awi.partner_id
            inner join res_company as rc on rc.id=awi.company_id
            inner join account_move as am on am.id=awi.invoice_rel
            left join account_withholding_rate_table_line as awrtl on awrtl.id=awil.table_id
            left join account_withholding_rate_table as awrt on awrt.id=awrtl.table_id
            WHERE awil.withholding_id is not null {date_clause}
                                """.format(date_clause=date_clause))
        self.env.cr.execute(sql_islr, query_params)
        query_result = self.env.cr.dictfetchall()
        
        concepto = []
        #raise UserError(query_result)
        if len(query_result) > 0:
            for row in query_result:
                monto_cheque = 0.00
                monto_sustraendo = 0.00
                retenido = row['retenido']
                
                if row['sustraendo'] == True:
                    if row['porcentaje_islr'] == 1:
                        monto_sustraendo = row['sus_1']
                    if row['porcentaje_islr'] == 3:
                        monto_sustraendo = row['sus_3']
                    #retenido = retenido - monto_sustraendo

                if row['cod'] not in concepto:
                    concepto.append(row['cod'])
                
                monto_cheque = row['monto_total'] - retenido

                final.append({
                    'comprobante': row['comprobante'],
                    'fecha': row['fecha'],
                    'proveedor': row['proveedor'],
                    'rif': row['rif'],
                    'monto_total': row['monto_total'],
                    'monto_base': row['monto_base'],
                    'porcentaje_islr': row['porcentaje_islr'],
                    'retenido': retenido,
                    'tipo_residencia': row['tipo_residencia'],
                    'descripcion': row['cod'],
                    'monto_sustraendo': monto_sustraendo,
                    'sustraendo': row['sustraendo'],
                    'factor': row['factor'],
                    'monto_cheque': monto_cheque,
                    })
        else:
            raise UserError(_("No hay datos para imprimir"))

        xls_filename = 'reporte_de_islr.xlsx'
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        header_merge_format = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':10, 'bg_color':'#D3D3D3', 'border':1})

        header_merge_format_titulo = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':16, 'bg_color':'#D3D3D3', 'border':1})

        header_data_format = workbook.add_format({'align':'center', 'valign':'vcenter', 'font_size':10, 'border':1})
        concepto_header = workbook.add_format({'align':'center', 'valign':'vcenter', 'font_size':10, 'bg_color':'#F1F1F1', 'border':1})
        currency_format = workbook.add_format({'align':'right', 'valign':'vcenter', 'font_size':10, 'border':1})

        header_data_format_titulo = workbook.add_format({'align':'center', 'valign':'vcenter', \
                                                   'font_size':12, 'border':1})

        currency_format = workbook.add_format({'num_format': '#,##0.00', 'font_size':10, 'border':1})

        fecha = workbook.add_format({'num_format': 'dd/mm/YYYY', 'border':1})

        worksheet = workbook.add_worksheet('ISLR Xlsx')

        worksheet.merge_range(0, 1, 1, 4, self.company_id.name, header_data_format_titulo)
        worksheet.merge_range(0, 6, 0, 7, 'Fecha de Impresión:', header_merge_format)
        worksheet.write_datetime(0,8, fields.Datetime.now(), fecha)

        worksheet.set_column('A:B', 18)
        worksheet.set_column('C:I', 12)

        worksheet.merge_range(4, 2, 6, 5,  'RETENCIONES DE I.S.L.R.', header_merge_format)
        #worksheet.write(8, 5, "Desde:", header_merge_format)
        #worksheet.write(8, 6, self.date_start, fecha)
        #worksheet.write(8, 7, "Hasta: ", header_merge_format)
        #worksheet.write(8, 8, self.date_end, fecha)

        row = 8

        if self.move_type=='out_invoice':
            worksheet.merge_range(row, 3, row, 4, "CUENTAS POR COBRAR", header_merge_format)
            row+=1
        
        if self.move_type=='in_invoice':
            worksheet.merge_range(row, 3, row, 4, "CUENTAS POR PAGAR", header_merge_format)
            row+=1
                
        if self.move_type=='in_refund':
            worksheet.merge_range(row, 3, row, 4, "NOTAS DE CREDITO / CUENTAS POR PAGAR", header_merge_format)
            row+=1
                
        if self.state:
            worksheet.merge_range(row, 3, row, 4, "Estatus: "+self.state, header_merge_format)
            row+=1
        
        if self.date_start and not self.date_end:
            if self.date_start:
                worksheet.write(row, 3, "Desde:", header_merge_format)
                worksheet.write(row, 4, self.date_start, fecha)
                row+=1
        
        if self.date_start and self.date_end:
            if self.date_start:
                worksheet.write(row, 3, "Desde:", header_merge_format)
                worksheet.write(row, 4, self.date_start, fecha)
                row+=1
            if self.date_end:
                worksheet.write(row, 3, "Hasta:", header_merge_format)
                worksheet.write(row, 4, self.date_end, fecha)
                row+=1
        if self.partner_id and (self.move_type=='in_invoice' or self.move_type=='in_refund'):
            worksheet.merge_range(row, 1, row, 6, "Proveedor: "+self.partner_id.name, header_merge_format)
            row+=1
        if self.partner_id and self.move_type=='out_invoice':
            worksheet.merge_range(row, 1, row, 6, "Cliente: "+self.partner_id.name, header_merge_format)
            row+=1
        
        row+=2
        worksheet.write(row, 0, "N°. COMP", header_merge_format)
        worksheet.write(row, 1, "FECHA", header_merge_format)
        worksheet.write(row, 2, "PROVEEDOR", header_merge_format)
        worksheet.write(row, 3, "NRO. RIF", header_merge_format)
        worksheet.write(row, 4, "MONTO CHEQUE", header_merge_format)
        worksheet.write(row, 5, "TOTAL FACTS.", header_merge_format)
        worksheet.write(row, 6, "TOTAL BASE", header_merge_format)
        worksheet.write(row, 7, "SUSTRAENDO", header_merge_format)
        worksheet.write(row, 8, "RETENIDO", header_merge_format)

        Tcont = 0.0
        TtotC = 0.0
        TtotF = 0.0
        TtotB = 0.0
        Tsus = 0.0
        Tret = 0.0
        #raise UserError(len(concepto))
        for c in concepto:
            ret = 0.0
            sus = 0.0
            totB = 0.0 #TOTAL BASE
            totF = 0.0 #TOTAL FACTURA
            totC = 0.0 #TOTAL CHEQUE
            cont = 0
            row+=1
            worksheet.merge_range(row, 0, row, 8, c, concepto_header)

            for f in final:
                if c==f['descripcion']:
                    cont += 1
                    Tcont = Tcont + 1
                    row+=1
                    worksheet.write(row, 0, f['comprobante'], header_data_format)
                    worksheet.write_datetime(row, 1, f['fecha'], fecha)
                    worksheet.write(row, 2, f['proveedor'], header_data_format)
                    worksheet.write(row, 3, f['rif'], header_data_format)
                    worksheet.write(row, 4, f['monto_cheque'], currency_format)
                    totC += f['monto_cheque']
                    TtotC += f['monto_cheque']
                    worksheet.write(row, 5, f['monto_total'], currency_format)
                    totF += f['monto_total']
                    TtotF += f['monto_total']
                    worksheet.write(row, 6, f['monto_base'], currency_format)
                    totB += f['monto_base']
                    TtotB += f['monto_base']
                    worksheet.write(row, 7, f['monto_sustraendo'], currency_format)
                    sus += f['monto_sustraendo']
                    Tsus += f['monto_sustraendo']
                    worksheet.write(row, 8, f['retenido'], currency_format)
                    ret += f['retenido']
                    Tret += f['retenido']

            worksheet.write(row+1, 2, 'TOTAL', header_data_format)
            worksheet.write(row+1, 3, cont, currency_format)
            worksheet.write(row+1, 4, totC, currency_format)
            worksheet.write(row+1, 5, totF, currency_format)
            worksheet.write(row+1, 6, totB, currency_format)
            worksheet.write(row+1, 7, sus, currency_format)
            worksheet.write(row+1, 8, ret, currency_format)
            row+=1

        worksheet.merge_range(row+1, 0, row+1, 2, 'TOTAL GENERAL', concepto_header)
        worksheet.write(row+1, 3, Tcont, currency_format)
        worksheet.write(row+1, 4, TtotC, currency_format)
        worksheet.write(row+1, 5, TtotF, currency_format)
        worksheet.write(row+1, 6, TtotB, currency_format)
        worksheet.write(row+1, 7, Tsus, currency_format)
        worksheet.write(row+1, 8, Tret, currency_format)
            
        
        
        
        
        
        
        





        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write({
            'states': 'get',
            'data': out,
            'name': xls_filename
        })
        return {
            'name': 'Libro de Compras',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

