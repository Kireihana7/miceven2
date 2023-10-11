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

class IvaXlsWizard(models.TransientModel):
    _name = 'iva.xls.wizard'

    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Proveedor o Cliente')
    state = fields.Selection([
        ('confirmed', 'Confirmado'),
        ('withhold', 'Retenido'),
        ('declared', 'Declarado'),
        ('done', 'Hecho'),
    ], string='Estatus de la retención')

    type_invoice = fields.Selection([
        ('in_invoice', 'Cuentas Por Pagar'),
        ('out_invoice', 'Cuentas Por Cobrar'),
    ], string='Retenciones de IVA', default='in_invoice', required=True,)

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
        vals = super(IvaXlsWizard, self).default_get(default_fields)
        vals['states'] = 'choose'
        return vals

    def go_back(self):
        self.states = 'choose'
        return {
            'name': 'IVA Excel',
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
        type_invoice_view = ''
        estatus_view = ''
        if self.date_start:
            date_clause += " AND awi.date >= %s"
            query_params.append(self.date_start)
        if self.date_end:
            date_clause += " AND awi.date <= %s"
            query_params.append(self.date_end)
        if self.partner_id:
            date_clause += " AND awi.partner_id = %s"
            query_params.append(self.partner_id.id)
        if self.state:
            date_clause += " AND awi.state = %s"
            query_params.append(self.state)
            if self.state == 'confirmed':
                estatus_view = 'Confirmado'
            elif self.state == 'withhold':
                estatus_view = 'Retenido'
            elif self.state == 'declared':
                estatus_view = 'Declarado'
            elif self.state == 'done':
                estatus_view = 'Hecho'

        if self.type_invoice:
            date_clause += " AND awi.move_type = %s"
            query_params.append(self.type_invoice)
            if self.type_invoice == 'in_invoice':
                type_invoice_view = 'Cuentas Por Pagar'
            else:
                type_invoice_view = 'Cuentas Por Cobrar'

        sql_iva = ("""        

            SELECT awi.number as comprobante, awi.date as fecha, am.name as factura, 
            (SELECT rif||'/'||name FROM res_partner WHERE id=awi.partner_id) as proveedor,
            am.amount_total as monto_total, SUM(awil.base_tax) as base_imponible, act.amount as iva, 
            SUM(awil.amount_tax) as impuesto, 
            awil.rate_amount as porcentaje, am.amount_wh_iva as monto, awi.state as estatus FROM
            account_tax as act 
            inner join account_wh_iva_line as awil on awil.ret_tax=act.id
            inner join account_wh_iva as awi on awi.id=awil.retention_id
            inner join account_move as am on am.wh_id=awi.id 
            WHERE awi.state!='annulled' and awi.state!='cancel' and awi.state!='draft' {date_clause}
            GROUP BY comprobante, fecha, factura, proveedor, iva, porcentaje, awi.state, monto, monto_total
            ORDER BY comprobante

                                """.format(date_clause=date_clause))
        self.env.cr.execute(sql_iva, query_params)
        query_result = self.env.cr.dictfetchall()
        
        if len(query_result)>0:
            for row in query_result:

                proveedor_rif = row['proveedor'].split('/')
                final.append({
                    'comprobante': row['comprobante'],
                    'fecha': row['fecha'],
                    'proveedor': proveedor_rif[1],
                    'rif': proveedor_rif[0],
                    'monto_total': row['monto_total'],
                    'base_imponible': row['base_imponible'],
                    'iva': row['iva'],
                    'impuesto': row['impuesto'],
                    'porcentaje': row['porcentaje'],
                    'monto': row['monto'],
                    'estatus': row['estatus'],
                    })
        else:
            raise UserError(_("No hay datos para imprimir"))

        xls_filename = 'reporte_de_iva.xlsx'
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

        worksheet = workbook.add_worksheet('IVA Xlsx')

        worksheet.merge_range(0, 1, 1, 4, self.company_id.name, header_data_format_titulo)
        worksheet.merge_range(0, 6, 0, 7, 'Fecha de Impresión:', header_merge_format)
        worksheet.write_datetime(0,8, fields.Datetime.now(), fecha)

        worksheet.set_column('A:B', 18)
        worksheet.set_column('C:I', 12)

        worksheet.merge_range(4, 2, 6, 5,  'RETENCIONES DE IVA', header_merge_format)

        row = 8

        if self.type_invoice=='out_invoice':
            worksheet.merge_range(row, 3, row, 4, "CUENTAS POR COBRAR", header_merge_format)
            row+=1
        
        if self.type_invoice=='in_invoice':
            worksheet.merge_range(row, 3, row, 4, "CUENTAS POR PAGAR", header_merge_format)
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
        if self.partner_id:
            worksheet.merge_range(row, 1, row, 6, "Proveedor: "+self.partner_id.name, header_merge_format)
            row+=1

        Tmonto = 0.0
        Tbase = 0.0
        Timpu = 0.0
        Ttot = 0.0                 
        comprobante_anterior=""

        row+=2
        worksheet.write(row, 0, "Comprobante", header_merge_format)
        worksheet.write(row, 1, "Feha", header_merge_format)
        worksheet.write(row, 2, "Proveedor", header_merge_format)
        worksheet.write(row, 3, "Rif", header_merge_format)
        worksheet.write(row, 4, "Monto", header_merge_format)
        worksheet.write(row, 5, "Base Imponible", header_merge_format)
        worksheet.write(row, 6, "% IVA", header_merge_format)
        worksheet.write(row, 7, "Impuesto", header_merge_format)
        worksheet.write(row, 8, "Porc.", header_merge_format)
        worksheet.write(row, 9, "Monto", header_merge_format)

        for f in final:                
            row+=1
            worksheet.write(row, 0, f['comprobante'], header_data_format)
            worksheet.write_datetime(row, 1, f['fecha'], fecha)
            worksheet.write(row, 2, f['proveedor'], header_data_format)
            worksheet.write(row, 3, f['rif'], header_data_format)
            worksheet.write(row, 4, f['monto_total'], currency_format)
            if f['comprobante'] != comprobante_anterior:
                Tmonto += f['monto_total']
            worksheet.write(row, 5, f['base_imponible'], currency_format)
            Tbase += f['base_imponible']
            worksheet.write(row, 6, f['iva'], currency_format)
            worksheet.write(row, 7, f['impuesto'], currency_format)
            Timpu += f['impuesto']
            worksheet.write(row, 8, f['porcentaje'], currency_format)
            Ttot += ((f['impuesto']*f['porcentaje'])/100)
            worksheet.write(row, 9, (f['impuesto']*f['porcentaje'])/100, currency_format)
            comprobante_anterior += f['comprobante']

        worksheet.write(row+1, 3, 'TOTAL GENERAL', header_data_format)  #rif
        worksheet.write(row+1, 4, Tmonto, currency_format)              #monto_total
        worksheet.write(row+1, 5, Tbase, currency_format)               #base_imponible
        worksheet.write(row+1, 6, '', currency_format)                  #iva
        worksheet.write(row+1, 7, Timpu, currency_format)               #impuesto
        worksheet.write(row+1, 8, '', header_data_format)               #porcentaje
        worksheet.write(row+1, 9, Ttot, currency_format)                #impuesto
            
        
        
        
        
        
        
        





        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write({
            'states': 'get',
            'data': out,
            'name': xls_filename
        })
        return {
            'name': 'Reporte de Retenciones de IVA en Excel',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

