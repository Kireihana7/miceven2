# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import io
from io import BytesIO
from odoo.exceptions import  UserError
import xlsxwriter
import shutil
import base64
import csv
import xlwt

class AccountReportConsolidate(models.TransientModel):
    _name = 'account.report.prorrateo'
    _description = "Report Prorrateo"

    from_date = fields.Date('From Date', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    journal_ids = fields.Many2many('account.journal', string='Journals',
       required=True,
       domain="['|',('type', '=', 'sale'),('type', '=', 'purchase')]",
       default=lambda self: self.env[
           'account.journal'].search(['|',('type', '=', 'sale'),('type', '=', 'purchase')]))

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],default='choose') ##Genera los botones de exportar xls y pdf como tambien el de cancelar
    #report = fields.Binary('Prepared file', filters='.xlsx', readonly=True)
    report = fields.Binary('File', readonly=True)
    name = fields.Char('File Name', size=32)

    def print_report(self):
        codes = []
        if self.journal_ids:
            codes = [journal.id for journal in self.journal_ids]
        domain = []
        datas = []
        datasp = []
        r33 = 0
        r34 = 0
        r333 = 0
        r343 = 0
        r332 = 0
        r342 = 0
        r40 = 0 # Ventas Internas No Gravadas BI
        r42 = 0 # Ventas Internas alicuota general BI
        r43 = 0
        r443 = 0
        r453 = 0
        r442 = 0
        r452 = 0
        r30 = 0
        r40 = 0
        r46 = 0 # Total Ventas y Debitos Fiscales BI
        r47 = 0 
        r35 = 0
        r36 = 0
        total_no_deducible_compra = 0
        r66 = 0
        r70= 0
        r49 = 0
        r90 = 0
        domain = [
        #'|',
        ('state', '=', 'posted'), 
        #('state', '=', 'cancel'), 
        ('date', '>=', self.from_date),
        ('company_id', '=', self.company_id.id),
        ('date', '<=', self.to_date),
        ('journal_id', 'in', codes)
        ]
        invoice = self.env["account.move"].search(domain,order='date asc')
        
        for move in invoice:
            r34_fact = 0
            r66 += move.amount_wh_iva if move.move_type == 'in_invoice' else 0
            for lines in move.invoice_line_ids:            
                if len(lines.tax_ids) == 0 or not lines.tax_ids or sum(lines.mapped('tax_ids.amount')) == 0: 
                    r30 += lines.price_subtotal if lines.move_id.move_type == 'in_invoice'   else 0
                    r40 += lines.price_subtotal if lines.move_id.move_type == 'out_invoice'  else 0
                    r30 -= lines.price_subtotal if lines.move_id.move_type == 'in_refund'   else 0
                    r40 -= lines.price_subtotal if lines.move_id.move_type == 'out_refund'  else 0
            
            # Calculos para Facturas (CON SUMA POR EL TIPO DE FACTURA)
            for lines in move.line_ids:
                if lines.tax_line_id:
                    if lines.tax_line_id.aliquot_type == 'reduced':
                        r333 += lines.tax_base_amount if lines.move_id.move_type == 'in_invoice'  else 0
                        r443 += lines.tax_base_amount if lines.move_id.move_type == 'out_invoice' else 0
                        r343 += lines.price_subtotal if move.move_type == 'in_invoice' else 0
                        r453 += lines.price_subtotal if move.move_type == 'out_invoice' else 0
                    if lines.tax_line_id.aliquot_type == 'general':
                        r33 += lines.tax_base_amount if lines.move_id.move_type == 'in_invoice'   else 0
                        r42 += lines.tax_base_amount if lines.move_id.move_type == 'out_invoice'  else 0
                        r34 += lines.price_subtotal if move.move_type == 'in_invoice' else 0
                        
                        r43 += lines.price_subtotal if move.move_type == 'out_invoice' else 0
                    if lines.tax_line_id.aliquot_type =='additional':
                        r332 += lines.tax_base_amount if lines.move_id.move_type == 'in_invoice'  else 0
                        r442 += lines.tax_base_amount if lines.move_id.move_type == 'out_invoice' else 0
                        r342 += lines.price_subtotal if move.move_type == 'in_invoice' else 0
                        r452 += lines.price_subtotal if move.move_type == 'out_invoice' else 0
            if move.deductible:
                total_no_deducible_compra += move.amount_tax  if move.move_type == 'in_invoice' else 0
                r34_fact += lines.price_subtotal if move.move_type == 'in_invoice' and lines.tax_line_id.aliquot_type == 'general' else 0
            
            # Calculos para Facturas (RESTANTE POR EL TIPO DE FACTURA)
            for lines in move.line_ids:
                if lines.tax_line_id:
                    if lines.tax_line_id.aliquot_type == 'reduced':
                        r333 -= lines.tax_base_amount if lines.move_id.move_type == 'in_refund'  else 0
                        r443 -= lines.tax_base_amount if lines.move_id.move_type == 'out_refund' else 0
                        r343 -= lines.price_subtotal if move.move_type == 'in_refund' else 0
                        r453 -= lines.price_subtotal if move.move_type == 'out_refund' else 0
                    if lines.tax_line_id.aliquot_type == 'general':
                        r33 -= lines.tax_base_amount if lines.move_id.move_type == 'in_refund'   else 0
                        r42 -= lines.tax_base_amount if lines.move_id.move_type == 'out_refund'  else 0
                        r34 -= lines.price_subtotal if move.move_type == 'in_refund' else 0
                        r43 -= lines.price_subtotal if move.move_type == 'out_refund' else 0
                    if lines.tax_line_id.aliquot_type =='additional':
                        r332 -= lines.tax_base_amount if lines.move_id.move_type == 'in_refund'  else 0
                        r442 -= lines.tax_base_amount if lines.move_id.move_type == 'out_refund' else 0
                        r342 -= lines.price_subtotal if move.move_type == 'in_refund' else 0
                        r452 -= lines.price_subtotal if move.move_type == 'out_refund' else 0
            if move.deductible:
                total_no_deducible_compra -= move.amount_tax if move.move_type == 'in_refund' else 0
                r34_fact -= lines.price_subtotal if move.move_type == 'in_refund' and lines.tax_line_id.aliquot_type == 'general' else 0

            if r34_fact != 0:
                datas.append({
                    'name':move.name,
                    'iva':r34_fact,
                })
                #raise UserError(('%s')%(r34_fact))
        r46 = r442 + r443 + r42 + r40
        r47 = r452 + r453 + r43 
        r49 = r47
        r35 = r332 + r333 + r33 + r30
        r36 = r342 + r343 + r34 
        r70 = r36 - total_no_deducible_compra
        r71 = r70
        r39 = r71
        r53 = r49-r39 if r49 > r39 else 0
        r60 = r39-r49 if r39 > r49 else 0
        r78 = r53
        r90 = r78
        if r40 != 0 and r46 != 0:
            proporcion_no_deducible = (r40/r46)
        else:
            proporcion_no_deducible = 0
        if r42 !=0 and r46 !=0:
            proporcion_deducible = (r42/r46)
        else:
            proporcion_deducible = 0
        #raise UserError(('%s,%s')%(proporcion_no_deducible,proporcion_deducible))
        res = {
            'start_date': self.from_date,
            'end_date': self.to_date,
            'company_name': self.company_id.name,
            'company_vat': self.company_id.vat,
            'company_street': self.company_id.street,
            'r30': r30,
            'r33': r33,
            'r34': r34,
            'r333': r333,
            'r343': r343,
            'r332': r332,
            'r342': r342,
            'r40': r40,
            'r42': r42,
            'r43': r43,
            'r443': r443,
            'r453': r453,
            'r442': r442,
            'r452': r452,
            'r46': r46,
            'r47': r47,
            'r35': r35,
            'r36': r36,
            'r66': r66,
            'total_no_deducible_compra':total_no_deducible_compra,
            'r70': r70,
            'r71': r71,
            'r49': r49,
            'r39': r39,
            'r53': r53,
            'r60': r60,
            'r78': r78,
            'r90': r90,
            'proporcion_no_deducible': proporcion_no_deducible,
            'proporcion_deducible': proporcion_deducible,
            'invoices':datas,
        }
        data = {
            'form': res,
            'datas': datas,
        }
        return self.env.ref('eu_prorrateo.acccount_report_prorrateo').report_action([],data=data)