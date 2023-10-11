# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import io
from io import BytesIO

import xlsxwriter
import shutil
import base64
import csv
import xlwt

class AccountReportConsolidate(models.TransientModel):
    _name = 'account.report.consolidate'
    _description = "Daily consolidate Report"

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
        domain_rete = []
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
        domain_rete = [
        #'|',
        ('state', '=', 'confirmed'), 
        #('state', '=', 'cancel'), 
        ('date', '>=', self.from_date),
        ('company_id', '=', self.company_id.id),
        ('date', '<=', self.to_date),
        ('move_type', '=', 'out_invoice')
        ]
        invoice = self.env["account.move"].search(domain,order='date asc')
        for rete in self.env['account.wh.iva'].search(domain_rete):
            r66 += rete.total_tax_ret * rete.manual_currency_exchange_rate

        for move in invoice:
            r34_fact = 0
            for lines in move.invoice_line_ids:            
                if move.currency_id == move.company_id.currency_id:
                    if len(lines.tax_ids) == 0 or not lines.tax_ids or sum(lines.mapped('tax_ids.amount')) == 0: 
                        r30 += lines.price_subtotal * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_invoice'   else 0
                        r40 += lines.price_subtotal * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_invoice'  else 0
                        r30 -= lines.price_subtotal * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_refund'   else 0
                        r40 -= lines.price_subtotal * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_refund'  else 0
                else:
                    if len(lines.tax_ids) == 0 or not lines.tax_ids or sum(lines.mapped('tax_ids.amount')) == 0: 
                        r30 += lines.price_subtotal if lines.move_id.move_type == 'in_invoice'   else 0
                        r40 += lines.price_subtotal if lines.move_id.move_type == 'out_invoice'  else 0
                        r30 -= lines.price_subtotal if lines.move_id.move_type == 'in_refund'   else 0
                        r40 -= lines.price_subtotal if lines.move_id.move_type == 'out_refund'  else 0
            
            # Calculos para Facturas (CON SUMA POR EL TIPO DE FACTURA)
            for lines in move.line_ids:
                if lines.tax_line_id:
                    if move.currency_id == move.company_id.currency_id:
                        if lines.tax_line_id.aliquot_type == 'reduced':
                            r333 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_invoice'  else 0
                            r443 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_invoice' else 0
                            r343 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' else 0
                            r453 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_invoice' else 0
                        if lines.tax_line_id.aliquot_type == 'general':
                            r33 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_invoice'   else 0
                            r42 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_invoice'  else 0
                            r34 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' else 0
                            r43 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_invoice' else 0
                        if lines.tax_line_id.aliquot_type =='additional':
                            r332 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_invoice'  else 0
                            r442 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_invoice' else 0
                            r342 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' else 0
                            r452 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_invoice' else 0
                    else:
                        if lines.tax_line_id.aliquot_type == 'reduced':
                            r333 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_invoice'  else 0
                            r443 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_invoice' else 0
                            r343 += lines.price_subtotal if move.move_type == 'in_invoice' else 0
                            r453 += lines.price_subtotal if move.move_type == 'out_invoice' else 0
                        if lines.tax_line_id.aliquot_type == 'general':
                            r33 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_invoice'   else 0
                            r42 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_invoice'  else 0
                            r34 += lines.price_subtotal if move.move_type == 'in_invoice' else 0
                            r43 += lines.price_subtotal if move.move_type == 'out_invoice' else 0
                        if lines.tax_line_id.aliquot_type =='additional':
                            r332 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_invoice'  else 0
                            r442 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_invoice' else 0
                            r342 += lines.price_subtotal if move.move_type == 'in_invoice' else 0
                            r452 += lines.price_subtotal if move.move_type == 'out_invoice' else 0
            if move.deductible:
                if move.currency_id == move.company_id.currency_id:
                    total_no_deducible_compra += move.amount_tax * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' else 0
                    r34_fact += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' and lines.tax_line_id.aliquot_type == 'general' else 0
                else:
                    total_no_deducible_compra += move.amount_tax  if move.move_type == 'in_invoice' else 0
                    r34_fact += lines.price_subtotal if move.move_type == 'in_invoice' and lines.tax_line_id.aliquot_type == 'general' else 0
            # Calculos para Facturas (RESTANTE POR EL TIPO DE FACTURA)
            for lines in move.line_ids:
                if lines.tax_line_id:
                    if move.currency_id == move.company_id.currency_id:
                        if lines.tax_line_id.aliquot_type == 'reduced':
                            r333 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_refund'  else 0
                            r443 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_refund' else 0
                            r343 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_refund' else 0
                            r453 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_refund' else 0
                        if lines.tax_line_id.aliquot_type == 'general':
                            r33 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_refund'   else 0
                            r42 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_refund'  else 0
                            r34 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_refund' else 0
                            r43 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_refund' else 0
                        if lines.tax_line_id.aliquot_type =='additional':
                            r332 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_refund'  else 0
                            r442 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_refund' else 0
                            r342 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_refund' else 0
                            r452 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_refund' else 0
                    else:
                        if lines.tax_line_id.aliquot_type == 'reduced':
                            r333 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_refund'  else 0
                            r443 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_refund' else 0
                            r343 -= lines.price_subtotal if move.move_type == 'in_refund' else 0
                            r453 -= lines.price_subtotal if move.move_type == 'out_refund' else 0
                        if lines.tax_line_id.aliquot_type == 'general':
                            r33 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_refund'   else 0
                            r42 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_refund'  else 0
                            r34 -= lines.price_subtotal if move.move_type == 'in_refund' else 0
                            r43 -= lines.price_subtotal if move.move_type == 'out_refund' else 0
                        if lines.tax_line_id.aliquot_type =='additional':
                            r332 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_refund'  else 0
                            r442 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_refund' else 0
                            r342 -= lines.price_subtotal if move.move_type == 'in_refund' else 0
                            r452 -= lines.price_subtotal if move.move_type == 'out_refund' else 0
            if move.deductible:
                if move.currency_id == move.company_id.currency_id:
                    total_no_deducible_compra -= move.amount_tax * move.manual_currency_exchange_rate if move.move_type == 'in_refund' else 0
                    r34_fact -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_refund' and lines.tax_line_id.aliquot_type == 'general' else 0
                else:
                    total_no_deducible_compra -= move.amount_tax if move.move_type == 'in_refund' else 0
                    r34_fact -= lines.price_subtotal if move.move_type == 'in_refund' and lines.tax_line_id.aliquot_type == 'general' else 0

            if r34_fact != 0:
                datas.append({
                    'name':move.name,
                    'iva':r34_fact,
                })
                #raise UserError(('%s')%(r34_fact))
        #raise UserError(r33)
        r46 = r442 + r443 + r42 + r40
        if r40 != 0 and r46 != 0:
            proporcion_no_deducible = (r40/r46)
        else:
            proporcion_no_deducible = 0
        if r42 !=0 and r46 !=0:
            proporcion_deducible = (r42/r46)
        else:
            proporcion_deducible = 0
        r47 = r452 + r453 + r43 
        r49 = r47
        r35 = r332 + r333 + r33 + r30
        r36 = r342 + r343 + r34 
        r37 = total_no_deducible_compra * proporcion_deducible
        r70 = r36 - total_no_deducible_compra
        r71 = r70 + r37
        r39 = r71
        r53 = r49-r39 if r49 > r39 else 0
        r60 = r39-r49 if r39 > r49 else 0
        r78 = r53
        r90 = r78
        
        
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
            'r37': r37,
            'proporcion_no_deducible': proporcion_no_deducible,
            'proporcion_deducible': proporcion_deducible,
            'invoices':datas,
        }
        data = {
            'form': res,
            'datas': datas,
        }
        return self.env.ref('account_daily_consolidate.account_daily_consolidate').report_action([],data=data)

    def generate_xls_report(self):

        codes = []
        if self.journal_ids:
            codes = [journal.id for journal in self.journal_ids]
        domain = []
        domain_rete = []
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
        domain_rete = [
        #'|',
        ('state', '=', 'confirmed'), 
        #('state', '=', 'cancel'), 
        ('date', '>=', self.from_date),
        ('company_id', '=', self.company_id.id),
        ('date', '<=', self.to_date),
        ('move_type', '=', 'out_invoice')
        ]
        invoice = self.env["account.move"].search(domain,order='date asc')
        for rete in self.env['account.wh.iva'].search(domain_rete):
            r66 += rete.total_tax_ret * rete.manual_currency_exchange_rate
        #r66 = sum(self.env['account.wh.iva'].search(domain_rete).mapped('total_tax_ret'))
        for move in invoice:
            r34_fact = 0
            #r66 += move.amount_wh_iva if move.move_type == 'in_invoice' else 0
            r34_fact = 0
            for lines in move.invoice_line_ids:            
                if move.currency_id == move.company_id.currency_id:
                    if len(lines.tax_ids) == 0 or not lines.tax_ids or sum(lines.mapped('tax_ids.amount')) == 0: 
                        r30 += lines.price_subtotal * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_invoice'   else 0
                        r40 += lines.price_subtotal * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_invoice'  else 0
                        r30 -= lines.price_subtotal * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_refund'   else 0
                        r40 -= lines.price_subtotal * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_refund'  else 0
                else:
                    if len(lines.tax_ids) == 0 or not lines.tax_ids or sum(lines.mapped('tax_ids.amount')) == 0: 
                        r30 += lines.price_subtotal if lines.move_id.move_type == 'in_invoice'   else 0
                        r40 += lines.price_subtotal if lines.move_id.move_type == 'out_invoice'  else 0
                        r30 -= lines.price_subtotal if lines.move_id.move_type == 'in_refund'   else 0
                        r40 -= lines.price_subtotal if lines.move_id.move_type == 'out_refund'  else 0
            
            # Calculos para Facturas (CON SUMA POR EL TIPO DE FACTURA)
            for lines in move.line_ids:
                if lines.tax_line_id:
                    if move.currency_id == move.company_id.currency_id:
                        if lines.tax_line_id.aliquot_type == 'reduced':
                            r333 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_invoice'  else 0
                            r443 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_invoice' else 0
                            r343 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' else 0
                            r453 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_invoice' else 0
                        if lines.tax_line_id.aliquot_type == 'general':
                            r33 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_invoice'   else 0
                            r42 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_invoice'  else 0
                            r34 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' else 0
                            r43 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_invoice' else 0
                        if lines.tax_line_id.aliquot_type =='additional':
                            r332 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_invoice'  else 0
                            r442 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_invoice' else 0
                            r342 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' else 0
                            r452 += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_invoice' else 0
                    else:
                        if lines.tax_line_id.aliquot_type == 'reduced':
                            r333 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_invoice'  else 0
                            r443 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_invoice' else 0
                            r343 += lines.price_subtotal if move.move_type == 'in_invoice' else 0
                            r453 += lines.price_subtotal if move.move_type == 'out_invoice' else 0
                        if lines.tax_line_id.aliquot_type == 'general':
                            r33 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_invoice'   else 0
                            r42 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_invoice'  else 0
                            r34 += lines.price_subtotal if move.move_type == 'in_invoice' else 0
                            r43 += lines.price_subtotal if move.move_type == 'out_invoice' else 0
                        if lines.tax_line_id.aliquot_type =='additional':
                            r332 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_invoice'  else 0
                            r442 += (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_invoice' else 0
                            r342 += lines.price_subtotal if move.move_type == 'in_invoice' else 0
                            r452 += lines.price_subtotal if move.move_type == 'out_invoice' else 0
            if move.deductible:
                if move.currency_id == move.company_id.currency_id:
                    total_no_deducible_compra += move.amount_tax * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' else 0
                    r34_fact += lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_invoice' and lines.tax_line_id.aliquot_type == 'general' else 0
                else:
                    total_no_deducible_compra += move.amount_tax  if move.move_type == 'in_invoice' else 0
                    r34_fact += lines.price_subtotal if move.move_type == 'in_invoice' and lines.tax_line_id.aliquot_type == 'general' else 0
            # Calculos para Facturas (RESTANTE POR EL TIPO DE FACTURA)
            for lines in move.line_ids:
                if lines.tax_line_id:
                    if move.currency_id == move.company_id.currency_id:
                        if lines.tax_line_id.aliquot_type == 'reduced':
                            r333 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_refund'  else 0
                            r443 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_refund' else 0
                            r343 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_refund' else 0
                            r453 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_refund' else 0
                        if lines.tax_line_id.aliquot_type == 'general':
                            r33 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_refund'   else 0
                            r42 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_refund'  else 0
                            r34 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_refund' else 0
                            r43 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_refund' else 0
                        if lines.tax_line_id.aliquot_type =='additional':
                            r332 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'in_refund'  else 0
                            r442 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) * move.manual_currency_exchange_rate if lines.move_id.move_type == 'out_refund' else 0
                            r342 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_refund' else 0
                            r452 -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'out_refund' else 0
                    else:
                        if lines.tax_line_id.aliquot_type == 'reduced':
                            r333 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_refund'  else 0
                            r443 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_refund' else 0
                            r343 -= lines.price_subtotal if move.move_type == 'in_refund' else 0
                            r453 -= lines.price_subtotal if move.move_type == 'out_refund' else 0
                        if lines.tax_line_id.aliquot_type == 'general':
                            r33 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_refund'   else 0
                            r42 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_refund'  else 0
                            r34 -= lines.price_subtotal if move.move_type == 'in_refund' else 0
                            r43 -= lines.price_subtotal if move.move_type == 'out_refund' else 0
                        if lines.tax_line_id.aliquot_type =='additional':
                            r332 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'in_refund'  else 0
                            r442 -= (lines.price_subtotal / (lines.tax_line_id.amount/100)) if lines.move_id.move_type == 'out_refund' else 0
                            r342 -= lines.price_subtotal if move.move_type == 'in_refund' else 0
                            r452 -= lines.price_subtotal if move.move_type == 'out_refund' else 0
            if move.deductible:
                if move.currency_id == move.company_id.currency_id:
                    total_no_deducible_compra -= move.amount_tax * move.manual_currency_exchange_rate if move.move_type == 'in_refund' else 0
                    r34_fact -= lines.price_subtotal * move.manual_currency_exchange_rate if move.move_type == 'in_refund' and lines.tax_line_id.aliquot_type == 'general' else 0
                else:
                    total_no_deducible_compra -= move.amount_tax if move.move_type == 'in_refund' else 0
                    r34_fact -= lines.price_subtotal if move.move_type == 'in_refund' and lines.tax_line_id.aliquot_type == 'general' else 0

            if r34_fact != 0:
                datas.append({
                    'name':move.name,
                    'iva':r34_fact,
                })
                #raise UserError(('%s')%(r34_fact))
        r46 = r442 + r443 + r42 + r40
        if r40 != 0 and r46 != 0:
            proporcion_no_deducible = (r40/r46)
        else:
            proporcion_no_deducible = 0
        if r42 !=0 and r46 !=0:
            proporcion_deducible = (r42/r46)
        else:
            proporcion_deducible = 0
        r47 = r452 + r453 + r43 
        r49 = r47
        r35 = r332 + r333 + r33 + r30
        r36 = r342 + r343 + r34 
        r37 = total_no_deducible_compra * proporcion_deducible
        r70 = r36 - total_no_deducible_compra
        r71 = r70 + r37
        r39 = r71
        r53 = r49-r39 if r49 > r39 else 0
        r60 = r39-r49 if r39 > r49 else 0
        r78 = r53
        r90 = r78

        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('Resumen')
        fp = BytesIO()

        header_content_style = xlwt.easyxf("font: name Helvetica size 20 px, bold 1, height 170;")
        header_content_style_c = xlwt.easyxf("font: name Helvetica size 20 px, bold 1, height 170; align: horiz center")
        sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin;")
        sub_header_style_c = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz center")
        sub_header_style_r = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz right")

        header_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170; borders: left thin, right thin, top thin, bottom thin;")
        header_style_c = xlwt.easyxf("font: name Helvetica size 10 px, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz center")
        header_style_r = xlwt.easyxf("font: name Helvetica size 10 px, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz right")

        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170;")
        row = 0
        col = 0
        ws1.row(row).height = 500
        # ************ cuerpo del excel
        ws1.write_merge(row,row, 4, 9, "Razón Social:"+" "+str(self.company_id.name), sub_header_style)
        row=row+1
        ws1.write_merge(row, row, 4, 9,"Rif:"+" "+str(self.company_id.vat), sub_header_style)
        row=row+1
        ws1.write_merge(row,row, 4, 9, "Resumen de IVA",sub_header_style_c)
        row=row+1
        ws1.write_merge(row,row, 4, 4, "Periodo",header_content_style)
        ws1.write_merge(row,row, 5, 5, " ",header_content_style)
        ws1.write_merge(row,row, 6, 6, "Desde:",header_content_style_c)
        ws1.write_merge(row,row, 7, 7, str(self.from_date),header_content_style)
        ws1.write_merge(row,row, 8, 8, "Hasta:",header_content_style_c)
        ws1.write_merge(row,row, 9, 9, str(self.to_date),header_content_style)

        row=row+2
        ws1.write_merge(row,row, 4, 7, "DÉBITOS FISCALES",sub_header_style)
        ws1.write_merge(row,row, 8, 8, "BASE IMPONIBLE",sub_header_style)
        ws1.write_merge(row,row, 9, 9, "DÉBITO FISCAL",sub_header_style)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-5),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Ventas Internas no Gravadas",header_style)
        ws1.write_merge(row,row, 8, 8, r40,header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-5),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Ventas de Exportación",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-5),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Ventas Internas Gravadas por Alicuota General",header_style)
        ws1.write_merge(row,row, 8, 8, r42,header_style_r)
        ws1.write_merge(row,row, 9, 9,r43,header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-5),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Ventas Internas Gravadas por Alicuota General más Adicional",header_style)
        ws1.write_merge(row,row, 8, 8, r442,header_style_r)
        ws1.write_merge(row,row, 9, 9, r452,header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-5),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Ventas Internas Gravadas por Alicuota Reducida",header_style)
        ws1.write_merge(row,row, 8, 8, r443,header_style_r)
        ws1.write_merge(row,row, 9, 9, r453,header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-5),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Total Ventas y Debitos Fiscales para Efectos de Determinación",header_style)
        ws1.write_merge(row,row, 8, 8, r46,header_style_r)
        ws1.write_merge(row,row, 9, 9, r47,header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-5),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Ajustes a los Débitos Fiscales de Periodos Anteriores.",header_style)
        ws1.write_merge(row,row, 8, 8, "---",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-5),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Certificados de Débitos Fiscales Exonerados",header_style)
        ws1.write_merge(row,row, 8, 8, "---",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-5),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Total Débitos Fiscales:",sub_header_style)
        ws1.write_merge(row,row, 8, 8, "---",sub_header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",sub_header_style_r)

        row=row+1
        ws1.write_merge(row,row, 4, 7, "CRÉDITO FISCALES",sub_header_style)
        ws1.write_merge(row,row, 8, 8, "BASE IMPONIBLE",sub_header_style)
        ws1.write_merge(row,row, 9, 9, "CRÉDITO FISCAL",sub_header_style)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Compras no Gravadas y/o sin Derecho a Credito Fiscal",header_style)
        ws1.write_merge(row,row, 8, 8, r30,header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Importaciones No Gravadas",header_style)
        ws1.write_merge(row,row, 8, 8,"0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Importaciones Gravadas por Alicuota General",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Importaciones Gravadas por Alicuota General más Alicuota Adicional",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Importaciones Gravadas por Alicuota Reducida",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Compras Gravadas por Alicuota General",header_style)
        ws1.write_merge(row,row, 8, 8, r33,header_style_r)
        ws1.write_merge(row,row, 9, 9, r34,header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Compras Gravadas por Alicuota General más Alicuota Adicional",header_style)
        ws1.write_merge(row,row, 8, 8, r332,header_style_r)
        ws1.write_merge(row,row, 9, 9, r342,header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Compras Gravadas por Alicuota Reducida",header_style)
        ws1.write_merge(row,row, 8, 8, r333,header_style_r)
        ws1.write_merge(row,row, 9, 9, r343,header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Total Compras y Créditos Fiscales del Período",header_style)
        ws1.write_merge(row,row, 8, 8, r35,header_style_r)
        ws1.write_merge(row,row, 9, 9, r36,header_style_r)

        row=row+1
        ws1.write_merge(row,row, 4, 9, "CALCULO DEL CREDITO DEDUCIBLE",sub_header_style)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Creditos Fiscales Totalmente Deducibles ",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Créditos Fiscales Producto de la Aplicación del Porcentaje de la Prorrata",header_style)
        ws1.write_merge(row,row, 8, 8, r37,header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Total Créditos Fiscales Deducibles",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Exedente Créditos Fiscales del Semana Anterior ",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Reintegro Solicitado (sólo exportadores)",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Reintegro (sólo quien suministre bienes o presten servicios a entes exonerados)",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Ajustes a los Créditos Fiscales de Periodos Anteriores.",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Certificados de Débitos Fiscales Exonerados (emitidos de entes exonerados) Registrados en el periodo",header_style)
        ws1.col(5).width = int(len('Certificados de Débitos Fiscales Exonerados (emitidos de entes exonerados) Registrados en el periodo')*128)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-6),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Total Creditos Fiscales:",sub_header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",sub_header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",sub_header_style_r)
        
        row=row+1
        ws1.write_merge(row,row, 4, 9, "AUTOLIQUIDACIÓN",sub_header_style)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-7),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Total Cuota Tributaria del Período.",header_style)
        ws1.write_merge(row,row, 8, 8, "---",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-7),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Exedente de Crédito Fiscal para el mes Siguiente.",header_style)
        ws1.write_merge(row,row, 8, 8, "---",header_style_r)
        ws1.write_merge(row,row, 9, 9,"0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-7),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Impuesto Pagado en Declaración(es) Sustituida(s)",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-7),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Retenciones Descontadas en Declaración(es) Sustitutiva(s)",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-7),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Percepciones Descontadas en Declaración(es) Sustitutiva(s)",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-7),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Sub- Total Impuesto a Pagar:",sub_header_style)
        #ws1.write_merge(row,row, 8, 8, "0,00",sub_header_style_r)
        ws1.write_merge(row,row, 9, 9,"0,00",sub_header_style_r)
        
        row=row+1
        ws1.write_merge(row,row, 4, 9, "RETENCIONES IVA",sub_header_style)
        #ws1.write_merge(row,row, 8, 8, "BASE IMPONIBLE",sub_header_style)
        #ws1.write_merge(row,row, 9, 9, "CRÉDITO FISCAL",sub_header_style)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-8),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Retenciones IVA Acumuladas por Descontar",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-8),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Retenciones del IVA del Periodo",header_style)
        ws1.write_merge(row,row, 8, 8,"0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-8),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Créditos del IVA Adquiridos por Cesiones de Retenciones",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-8),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Recuperaciones del IVA Retenciones Solicitadas",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-8),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Total Retenciones del IVA",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-8),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Retenciones del IVA Soportadas y Descontadas",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-8),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Saldo Retenciones del IVA no Aplicado ",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-8),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Sub- Total Impuesto a Pagar item 40:",sub_header_style)
        ws1.write_merge(row,row, 9, 9,"0,00",sub_header_style_r)

        row=row+1
        ws1.write_merge(row,row, 4, 9, "PERCEPCIÓN",sub_header_style)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-9),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Percepciones Acumuladas en Importaciones por Descontar",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-9),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Percepciones del Periodo",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-9),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Créditos Adquiridos por Cesiones de Percepciones",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-9),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Recuperaciones Percepciones Solicitado",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-9),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Total Percepciones",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-9),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Percepciones en Aduanas Descontadas",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-9),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Saldo de Percepciones en Aduanas no Aplicado",header_style)
        ws1.write_merge(row,row, 8, 8, "0,00",header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",header_style_r)
        row=row+1
        ws1.write_merge(row,row, 4, 4, (row-9),header_style_c)
        ws1.write_merge(row,row, 5, 7,"Total a Pagar:",sub_header_style)
        #ws1.write_merge(row,row, 8, 8, "0,00",sub_header_style_r)
        ws1.write_merge(row,row, 9, 9, "0,00",sub_header_style_r)
        # ************ fin cuerpo excel
        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        fecha  = datetime.now().strftime('%d/%m/%Y') 
        fp.close()
        self.write({'state': 'get', 'report': out, 'name':'Resumen_Articulo_72.xls'})
        #return {
        #    'type': 'ir.actions.act_window',
        #    'res_model': 'account.report.consolidate',
        #    'view_mode': 'form',
        #    'view_type': 'form',
        #    'res_id': self.id,
        #    'views': [(False, 'form')],
        #    'target': 'new',
        #}
        #return {
        #    'name': 'Resumen Articulo 72',
        #    'type': 'ir.actions.act_window',
        #    'res_model': 'account.report.consolidate',
        #    'view_mode': 'form',
        #    'res_id': self.id,
        #    'target': 'new'
        #}
        name= "Resumen_Articulo_72"
        name += '%2Exls'
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model='+self._name+'&id='+str(self.id)+'&field=report&download=true&filename='+name,
        }