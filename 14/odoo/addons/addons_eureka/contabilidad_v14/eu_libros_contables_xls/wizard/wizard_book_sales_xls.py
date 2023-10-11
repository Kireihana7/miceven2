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

import time
from datetime import timedelta, datetime, date

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError
import xlsxwriter
import base64
from io import BytesIO
import pytz
import datetime

class WizardBookSalesXls(models.TransientModel):
    _name = 'book.sales.xls.wizard'
    _description = "Libro de Ventas Excel"
    
    name = fields.Char(string='Nombre del Archivo', readonly=True)
    data = fields.Binary(string='Archivo', readonly=True)    
    states = fields.Selection([
        ('choose', 'choose'), 
        ('get', 'get')], 
        default='choose')
    account_ids = fields.Many2many('account.account',
                                   'account_report_sales_account_rel_two',
                                   'report_id', 'account_id',
                                   'Accounts')
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env.user.company_id)
    display_account = fields.Selection(
        [('all', 'All'), ('movement', 'With movements'),
         ('not_zero', 'With balance is not equal to 0')],
        string='Display Accounts', required=True, default='movement')
    date_to = fields.Date(string='End Date', default=date.today())
    date_from = fields.Date(string='Start Date', default=date.today())
    journal_ids = fields.Many2many('account.journal', string='Journals',
                                   required=True,
                                   default=lambda self: self.env[
                                       'account.journal'].search([('type', '=', 'sale')]))
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries')], string='Target Moves', required=True,
                                   default='posted')
    sortby = fields.Selection(
        [('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')],
        string='Sort by',
        required=True, default='sort_date')

    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    in_bs = fields.Boolean(string="Mostrar en Bs",default=True) 

    #def _domain_branch_ids(self):
    #    return [('id','in',(self.env.user.branch_ids.ids))]
    #branch_ids = fields.Many2many('res.branch', string='Sucursales',
    #                               required=True,
    #                               default=lambda self: self.env.user.branch_ids,domain=_domain_branch_ids)

    @api.model
    def default_get(self, default_fields):
        vals = super(WizardBookSalesXls, self).default_get(default_fields)
        vals['states'] = 'choose'
        return vals

    def go_back(self):
        self.states = 'choose'
        return {
            'name': 'Libro de Ventas Excel',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    def _build_contexts(self, data):
        results = {}
        results['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        results['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        results['date_from'] = data['form']['date_from'] or False
        results['date_to'] = data['form']['date_to'] or False
        results['strict_range'] = True if results['date_from'] else False
        results['currency_id'] = data['form']['currency_id'] or False
        results['in_bs'] = data['form']['in_bs'] or False
        return results


    def print_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = \
        self.read(['date_from', 'date_to', 'journal_ids', 'target_move','display_account','account_ids','sortby','currency_id'])[0]
        #self.read(['date_from', 'date_to', 'journal_ids'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context,lang=self.env.context.get('lang') or 'es_ES')
        return self.env.ref('eu_libros_contables_xls.book_sale_xls').report_action(self,data=data)

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        '''
        This method validated that the final date is not less than the initial date
        :return:
        '''
        if self.date_to < self.date_from:
            raise UserError(_("The end date cannot be less than the start date "))

    def _get_account_move_entry(self, accounts, form_data, sortby, pass_date, display_account):
        cr = self.env.cr
        aml = self.env['account.move.line']

        tables, where_clause, where_params = aml._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        if form_data['target_move'] == 'posted':
            target_move = "AND m.state = 'posted'"
        else:
            target_move = ''
        sql = ('''
                SELECT l.id AS lid, acc.name as accname, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, 
                l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, 
                COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,
                m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                JOIN account_account acc ON (l.account_id = acc.id) 
                WHERE l.account_id IN %s AND l.journal_id IN %s AND l.date = %s
                GROUP BY l.id, l.account_id, l.date,
                     j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name , acc.name
                     ORDER BY l.date DESC
        ''')
        params = (
            tuple(accounts.ids), tuple(form_data['journal_ids']), pass_date)
        cr.execute(sql, params)
        data = cr.dictfetchall()

        
        res = {}
        debit = credit = balance = 0.00
        for line in data:
            debit += line['debit']
            credit += line['credit']
            balance += line['balance']
        res['debit'] = debit
        res['credit'] = credit
        res['balance'] = balance
        res['lines'] = data
        return res

    @api.model
    def _get_report_values(self, data=None):
        #if not data.get('form') or not self.env.context.get('active_model'):
        #    raise UserError(_("Form content is missing, this report cannot be printed."))
        sortby = data['form'].get('sortby')
        #las retenciones
        form_data = data['form']
        target_mov = ('posted','cancel') if form_data['target_move'] =='posted' else ('draft','cancel','posted')
        currency_id = self.env['res.currency'].browse([form_data['currency_id'][0]])
        company_id = self.env.company
        active_acc = data['form']['account_ids']
        in_bs = data['form'].get('in_bs')
        accounts = self.env['account.account'].search([('id', 'in', active_acc)]) if data['form']['account_ids'] else self.env['account.account'].search([])
        date_start = datetime.datetime.strptime(str(form_data['date_from']),'%Y-%m-%d')
        date_end = datetime.datetime.strptime(str(form_data['date_to']), '%Y-%m-%d')
        date_start = fields.Datetime.context_timestamp(self,date_start)
        
        
        docs_ret = self.env['account.wh.iva'].search([('move_type', 'in', ('out_invoice', 'out_refund'))])
        #las facturas in_invoice y las facturas rectificativas out_refund
        #esta linea aplica todos los filtros
        docs_fac = self.env['account.move'].search([('move_type', 'in', ('out_refund', 'out_invoice')),
                                                     ('date', '<=', self.date_to),
                                                     ('date', '>', date_start),
                                                     ('currency_id', '=', currency_id.id),
                                                     ('state', 'in', target_mov),
                                                     ('journal_id', 'in', form_data['journal_ids'])]).sorted(key=lambda x: x.journal_id.id and x.partner_id.name if sortby == 'sort_journal_partner' else x.date).filtered(lambda c: c.line_ids.mapped('account_id') & accounts != self.env['account.account'])
        rete = self.env['account.wh.iva.line'].search([
                                        ('retention_id.date', '>', date_start),
                                        ('retention_id.date', '<=', self.date_to),
                                        ('retention_id.move_type', 'in', ('out_invoice','out_refund')),
                                        ('state', 'not in', ('draft','anulled')),
                                        ('retention_id.company_id','=',self.env.company.id),
                                        ])
        print('prueba')
        print('prueba')
        print('prueba')
        print(docs_fac.line_ids)

        if not docs_fac:
            raise UserError('No se encontraron registros con estas características durante el periodo seleccionado. Verifique los datos ingresados.')
        #model = self.env.context.get('active_model')
        display_account = 'movement'
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]



        # days = self.date_to - date_start
        dates = []
        record = []
        # for i in range(days.days + 1):
        #     dates.append(date_start + timedelta(days=i))
        for head in dates:
            pass_date = str(head)
            accounts_res = self.with_context(
                data['form'].get('used_context', {}))._get_account_move_entry(
                accounts, form_data, sortby,pass_date, display_account)
            if accounts_res['lines']:
                record.append({
                    'date': head,
                    'debit': accounts_res['debit'],
                    'credit': accounts_res['credit'],
                    'balance': accounts_res['balance'],
                    'child_lines': accounts_res['lines']
                })
        hora_printer = (datetime.datetime.now()).astimezone(pytz.timezone(self.env.user.tz)).strftime('%I:%M:%S %p')
        print ('data')
        print (data)
        return {
            #'doc_ids': docids,
            #'doc_model': model,
            'data': data['form'],
            'docs': docs_ret,
            'rete': rete,
            'fact': docs_fac,
            'time': time,
            'hora_printer': hora_printer,
            'Accounts': record,
            'print_journal': codes,
            'currency_id': currency_id,
            'company_id': company_id,
            'company_vat':  company_id.vat[:10]+'-'+company_id.vat[10:] if company_id.vat else 'S/R',
            'in_bs':in_bs,
        }

    def print_xls_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = \
        self.read(['date_from', 'date_to', 'journal_ids', 'target_move','display_account','account_ids','sortby','in_bs','currency_id'])[0]
        #self.read(['date_from', 'date_to', 'journal_ids'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context,lang=self.env.context.get('lang') or 'es_ES')
        xls_filename = 'libro_ventas.xlsx'
        fp = BytesIO()

        #branch_name=self.branch_ids.mapped("name")
        
        
        workbook = xlsxwriter.Workbook(fp)
        

        header_merge_format = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':10, 'bg_color':'#D3D3D3', 'border':1})

        header_merge_format_titulo = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':16, 'bg_color':'#D3D3D3', 'border':1})

        header_data_format = workbook.add_format({'align':'center', 'valign':'vcenter', 'font_size':10, 'border':1})
        currency_format = workbook.add_format({'align':'right', 'valign':'vcenter', 'font_size':10, 'border':1})

        header_data_format_titulo = workbook.add_format({'align':'center', 'valign':'vcenter', \
                                                   'font_size':12, 'border':1})

        currency_format = workbook.add_format({'num_format': '#,##0.00', 'font_size':10, 'border':1})

        fecha = workbook.add_format({'num_format': 'dd/mm/YYYY', 'border':1})

        worksheet = workbook.add_worksheet('Libro de Ventas Xlsx')

        worksheet.merge_range(0, 1, 1, 4, self.company_id.name, header_data_format_titulo)
        worksheet.merge_range(0, 6, 0, 7, 'Fecha de Impresión:', header_merge_format)
        worksheet.write_datetime(0,8, fields.Datetime.now(), fecha)

        worksheet.set_column('A:B', 18)
        worksheet.set_column('C:I', 12)

        worksheet.merge_range('F4:H4', ", ", header_merge_format)
        worksheet.merge_range(4, 3, 6, 10,  'LIBRO DE VENTAS', header_merge_format_titulo)
        worksheet.write(8, 5, "Desde:", header_merge_format)
        worksheet.write(8, 6, data['form']['date_from'], fecha)
        worksheet.write(8, 7, "Hasta: ", header_merge_format)
        worksheet.write(8, 8, data['form']['date_to'], fecha)

        worksheet.write(10, 0, "Oper. N°", header_merge_format)
        worksheet.write(10, 1, "Fecha de la Factura", header_merge_format)
        worksheet.write(10, 2, "RIF o Cedula", header_merge_format)
        worksheet.write(10, 3, "Nombre o Razón Social", header_merge_format)
        worksheet.write(10, 4, "Numero de Factura", header_merge_format)
        worksheet.write(10, 5, "Serie", header_merge_format)
        worksheet.write(10, 6, "Núm. Ctrol. de Factura", header_merge_format)
        worksheet.write(10, 7, "Número Nota Debito", header_merge_format)
        worksheet.write(10, 8, "Número Planilla de Exportacion", header_merge_format)
        worksheet.write(10, 9, "Número de Expediente Exportacion", header_merge_format)
        worksheet.write(10, 10, "Número de Nota Credito", header_merge_format)
        worksheet.write(10, 11, "Tipo de Transacción", header_merge_format)
        worksheet.write(10, 12, "Número de Factura Afectada", header_merge_format)
        worksheet.write(10, 13, "Total Ventas Incluyendo el IVA", header_merge_format)
        worksheet.write(10, 14, "Ventas Exentas o Exoneradas", header_merge_format)
        worksheet.write(10, 15, "Base Imponible", header_merge_format)
        worksheet.write(10, 16, "% Alicuota", header_merge_format)
        worksheet.write(10, 17, "Impuesto IVA", header_merge_format)
        worksheet.write(10, 18, "Ventas Exentas o Exonerada", header_merge_format)
        worksheet.write(10, 19, "Base Imponible", header_merge_format)
        worksheet.write(10, 20, "% Alícuota", header_merge_format)
        worksheet.write(10, 21, "Impuesto IVA", header_merge_format)
        worksheet.write(10, 22, "IVA Retenido por el Comprador", header_merge_format)
        worksheet.write(10, 23, "Comprobante de Retencion", header_merge_format)
        worksheet.write(10, 24, "IVA Percibido", header_merge_format)

        R40 = 0
        R41 = 0
        R42 = 0
        R43 = 0
        R442 = 0
        R452 = 0
        R443 = 0
        R453 = 0
        R46 = 0
        R47 = 0
        R54 = 0
        R62 = 0
        R34 = 0
        R35 = 0
        R36 = 0
        untaxed = 0
        exento=0
        tax=0
        retencion = 0.00
        total = 0.00
        iva_percibido = 0
        iva_percibido_g = 0
        iva_percibido_r = 0
        iva_percibido_ga = 0
        retencion_g = 0
        retencion_ga = 0
        retencion_r = 0
        retention = 0
        monto_impuesto_untaxed_exento = 0
        acum_exento=0

        rows = 10
        cont = 0
        if not data['form']['in_bs']:
            dict_fact = self._get_report_values(data)
            facs = dict_fact['fact'].filtered(lambda doc: doc.transaction_type != '04-ajuste')
            base_imponible_total = 0
            total_exentas=0
            for s in facs.filtered('invoice_date').sorted(lambda m: (m.invoice_date, m.name)):
                rows += 1            
                cont += 1
                if s.doc_impor_export:
                    if s.state !='annulled' and s.state !='cancel':
                        if s.retention == '01-sin':
                            retention = 0
                        if s.retention == '02-special':
                            retention = 0.75
                        if s.retention == '03-ordinary':
                            retention = 1

                        # COMIENZAN LOS CALCULOS
                        if s.move_type == 'out_invoice':
                            total = total + sum(s.mapped('amount_total'))
                        if s.move_type == 'out_refund':
                            total = total - sum(s.mapped('amount_total'))
                        #Calculamos el Exento
                        exento = sum(s.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))
                        #IMPUESTOS REDUCIDOS
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced')))):
                            #BASE IMPONIBLE DEL IMPUESTO
                            if s.move_type == 'out_invoice':
                                R41 = R41 + sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))
                            if s.move_type == 'out_refund':
                                R41 = R41 - sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))
    
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR-->
                                if s.move_type == 'out_refund': 
                                    retencion_r = retencion_r-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice': 
                                    retencion_r = retencion_r+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund':
                                    iva_percibido_r = iva_percibido_r-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice':
                                    iva_percibido_r = iva_percibido_r+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                    
                        #IMPUESTOS ADICIONALES                
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional')))):
                            #Base imponible del Impuesto
                            if s.move_type == 'out_invoice': 
                                R41= R41 +sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))
                            if s.move_type == 'out_refund': 
                                R41= R41 -sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))
                            #Monto del Impuesto
        
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR-->
                                if s.move_type == 'out_refund':
                                    retencion_ga = retencion_ga-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice':
                                    retencion_ga =retencion_ga+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund': 
                                    iva_percibido_ga = iva_percibido_ga-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice': 
                                    iva_percibido_ga = iva_percibido_ga+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                        
                        #IMPUESTOS GENERALES
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general')))):
                            #Base imponible del Impuesto
                            if s.move_type == 'out_invoice':
                                R41= R41 +sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))
                            if s.move_type == 'out_refund':
                                R41= R41 -sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))

                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                            #IVA RETENIDO POR EL COMPRADOR
                                if s.move_type == 'out_refund':
                                    retencion_g = retencion_g-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice':
                                    retencion_g = retencion_g+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund':
                                    iva_percibido_g = iva_percibido_g-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice':
                                    iva_percibido_g = iva_percibido_g+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))

                        #Calculamos el TOTAL de impuestos EXENTOS
                        if s.move_type == 'out_invoice':
                            untaxed = untaxed + exento
                        if s.move_type == 'out_refund':
                            untaxed = untaxed - exento
                        if s.move_type == 'out_invoice':
                            R41 = R41 + exento
                        if s.move_type == 'out_refund':
                            R41 = R41 - exento
                        #Retenciones
                        if s.move_type == 'out_invoice':
                            retencion = retencion + s.wh_id.total_tax_ret
                        if s.move_type == 'out_refund':
                            retencion = retencion - s.wh_id.total_tax_ret
                        #TOTAL de IMPUESTOS (Reducido + General + Adicional)
                        if s.move_type == 'out_invoice':
                            tax = tax + s.amount_tax
                        if s.move_type == 'out_refund':
                            tax = tax - s.amount_tax
                        #IVA PERCIBIDO
                        if s.move_type == 'out_invoice':
                            iva_percibido = iva_percibido+((s.amount_tax)-(s.wh_id.total_tax_ret))
                        if s.move_type == 'out_refund':
                            iva_percibido = iva_percibido-((s.amount_tax)-(s.wh_id.total_tax_ret))
                        #TERMINAN LOS CALCULOS
                else:
                    if s.state !='annulled' and s.state !='cancel':
                        if s.retention == '01-sin':
                            retention = 0
                        if s.retention == '02-special':
                            retention = 0.75
                        if s.retention == '03-ordinary':
                            retention = 1

                        # COMIENZAN LOS CALCULOS
                        if s.move_type == 'out_invoice':
                            total = total + sum(s.mapped('amount_total'))
                        if s.move_type == 'out_refund':
                            total = total - sum(s.mapped('amount_total'))
                        #Calculamos el Exento
                        exento = sum(s.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))
                        #IMPUESTOS REDUCIDOS
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced')))):
                            #BASE IMPONIBLE DEL IMPUESTO
                            if s.move_type == 'out_invoice':
                                R443 = R443 + sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))
                            if s.move_type == 'out_refund':
                                R443 = R443 - sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))
                            #MONTO DEL IMPUESTO
                            if s.move_type == 'out_invoice':
                                R453 = R453 + (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))
                            if s.move_type == 'out_refund':
                                R453 = R453 - (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))
                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR-->
                                if s.move_type == 'out_refund': 
                                    retencion_r = retencion_r-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice': 
                                    retencion_r = retencion_r+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund':
                                    iva_percibido_r = iva_percibido_r-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice':
                                    iva_percibido_r = iva_percibido_r+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                    
                        #IMPUESTOS ADICIONALES                
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional')))):
                            #Base imponible del Impuesto
                            if s.move_type == 'out_invoice': 
                                R442= R442 +sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))
                            if s.move_type == 'out_refund': 
                                R442= R442 -sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))
                            #Monto del Impuesto
                            if s.move_type == 'out_invoice':
                                R452= R452 + (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))
                            if s.move_type == 'out_refund':
                                R452= R452 - (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))
                        
                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR-->
                                if s.move_type == 'out_refund':
                                    retencion_ga = retencion_ga-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice':
                                    retencion_ga =retencion_ga+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund': 
                                    iva_percibido_ga = iva_percibido_ga-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice': 
                                    iva_percibido_ga = iva_percibido_ga+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                        
                        #IMPUESTOS GENERALES
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general')))):
                            #Base imponible del Impuesto
                            if s.move_type == 'out_invoice':
                                R42= R42 +sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))
                            if s.move_type == 'out_refund':
                                R42= R42 -sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))
                            #Monto del Impuesto
                            if s.move_type == 'out_invoice':
                                R43 = R43 + (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))
                            if s.move_type == 'out_refund':
                                R43 = R43 - (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                            #IVA RETENIDO POR EL COMPRADOR
                                if s.move_type == 'out_refund':
                                    retencion_g = retencion_g-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice':
                                    retencion_g = retencion_g+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund':
                                    iva_percibido_g = iva_percibido_g-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice':
                                    iva_percibido_g = iva_percibido_g+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))

                        #Calculamos el TOTAL de impuestos EXENTOS
                        if s.move_type == 'out_invoice':
                            untaxed = untaxed + exento
                        if s.move_type == 'out_refund':
                            
                            untaxed = untaxed - exento
                        if s.move_type == 'out_invoice':
                            R40 = R40 + exento
                        if s.move_type == 'out_refund':
                            R40 = R40 - exento
                        #Retenciones
                        if s.move_type == 'out_invoice':
                            retencion = retencion + s.wh_id.total_tax_ret
                        if s.move_type == 'out_refund':
                            retencion = retencion - s.wh_id.total_tax_ret
                        #TOTAL de IMPUESTOS (Reducido + General + Adicional)
                        if s.move_type == 'out_invoice':
                            tax = tax + s.amount_tax
                        if s.move_type == 'out_refund':
                            tax = tax - s.amount_tax
                        #IVA PERCIBIDO
                        if s.move_type == 'out_invoice':
                            iva_percibido = iva_percibido+((s.amount_tax)-(s.wh_id.total_tax_ret))
                        if s.move_type == 'out_refund':
                            iva_percibido = iva_percibido-((s.amount_tax)-(s.wh_id.total_tax_ret))
                        #TERMINAN LOS CALCULOS

                worksheet.write(rows, 0, cont, header_data_format)
                worksheet.write_datetime(rows,1, s.invoice_date, fecha)
                worksheet.write(rows, 2, s.partner_id.rif, header_data_format)
                worksheet.write(rows, 3, s.partner_id.name, header_data_format)
                
                worksheet.write(rows, 4, '-' if s.transaction_type in ('02-complemento','03-anulacion') else int(s.name) if len(s.name) <= 6 else s.name, header_data_format)
                
                worksheet.write(rows, 5, 'Serie '+s.account_serie.upper() if s.account_serie else '-', header_data_format)
                if s.move_type=='out_invoice':
                    worksheet.write(rows, 6, s.nro_control, header_data_format)
                if s.move_type == 'out_refund':
                    worksheet.write(rows, 6, s.ref_credit, header_data_format)
                
                worksheet.write(rows, 7,'-', header_data_format)
                worksheet.write(rows, 8, s.num_import, header_data_format)                       #Número de Planilla de Importación
                worksheet.write(rows, 9, s.num_export, header_data_format)                       #Número de Expediente Importación
                worksheet.write(rows, 10, s.num_credit if s.move_type == 'out_refund' else '-', header_data_format)
                worksheet.write(rows, 11, s.transaction_type, header_data_format)
                worksheet.write(rows, 12, s.reversed_entry_id.name if s.move_type == 'out_refund' else '-', header_data_format)
                worksheet.write(rows, 13, sum(s.mapped('amount_total'))*-1 if s.move_type == 'out_refund' else sum(s.mapped('amount_total')), currency_format)


                monto_impuesto = sum(s.invoice_line_ids.mapped('tax_ids.amount'))
                monto_impuesto_untaxed = sum(s.invoice_line_ids.filtered(lambda whl: not whl.tax_ids).mapped('price_subtotal')) + sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))
                monto_impuesto_untaxed_exento = sum(s.invoice_line_ids.filtered(lambda whl: len(whl.tax_ids) == 0).mapped('price_subtotal'))
                if monto_impuesto == 0 or monto_impuesto_untaxed > 0 or monto_impuesto_untaxed_exento:
                    worksheet.write(rows,14, exento*-1 if s.move_type == 'in_refund' else exento, currency_format)
                    acum_exento += (exento)
                else:
                    worksheet.write(rows,14, 0.0, currency_format)
                
                if sum(s.invoice_line_ids.mapped('tax_ids.amount')) > 0:
                    #worksheet.write(rows, 13, sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids) > 0).mapped('price_subtotal')) * -1 if s.move_type == 'out_refund' else sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids) > 0).mapped('price_subtotal')), currency_format)
                    worksheet.write(rows, 15, sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids.filtered(lambda imp: imp.amount > 0))>0).mapped('price_subtotal')) *-1 if s.move_type == 'out_refund' else sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids.filtered(lambda imp: imp.amount > 0))>0).mapped('price_subtotal')), currency_format)

                    #MODIFICADO PARA QUE TOME EN CUENTA LAS NOTAS DE CREDITO Y RESTE
                    if s.move_type == 'out_invoice':
                        base_imponible_total = base_imponible_total + sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids.filtered(lambda imp: imp.amount >0))>0).mapped('price_subtotal'))
                    if s.move_type == 'out_refund':
                        base_imponible_total = base_imponible_total - sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids.filtered(lambda imp: imp.amount >0))>0).mapped('price_subtotal'))
                

                else:
                    worksheet.write(rows, 15, 0.00, currency_format)
                worksheet.write(rows, 16, sum(s.invoice_line_ids.mapped('tax_ids.amount')), currency_format)
                worksheet.write(rows, 17, s.amount_tax*-1 if s.move_type == 'out_refund' else s.amount_tax, currency_format)
                worksheet.write(rows, 18, '', header_data_format )
                worksheet.write(rows, 19, '', header_data_format)
                worksheet.write(rows, 20, '', header_data_format)
                worksheet.write(rows, 21, '', header_data_format)
                worksheet.write(rows, 22, '', header_data_format)
                worksheet.write(rows, 23, '', header_data_format)
                worksheet.write(rows, 24, ((s.amount_tax)-(s.wh_id.total_tax_ret))*-1 if s.move_type == 'out_refund' else (s.amount_tax)-(s.wh_id.total_tax_ret), currency_format)

                if s.state =='cancel':
                    worksheet.write(rows, 0, cont, header_data_format)
                    worksheet.write_datetime(rows,1, s.invoice_date, fecha)
                    worksheet.write(rows, 2, s.partner_id.rif, header_data_format)
                    worksheet.write(rows, 3, s.partner_id.name, header_data_format)
                    worksheet.write(rows, 4, '-' if s.transaction_type in ('02-complemento','03-anulacion') else int(s.name) if len(s.name) <= 6 else s.name, header_data_format)
                    worksheet.write(rows, 5, 'Serie '+s.account_serie.upper() if s.account_serie else '-', header_data_format)
                    worksheet.write(rows, 6, s.nro_control if s.nro_control else '-', header_data_format)
                    worksheet.write(rows, 7, '-', header_data_format)
                    worksheet.write(rows, 8, '-', header_data_format)
                    worksheet.write(rows, 9, '-', header_data_format)
                    worksheet.write(rows, 10, s.num_credit if s.move_type == 'out_refund' else '-', header_data_format)
                    worksheet.write(rows, 11, s.transaction_type, header_data_format)
                    worksheet.write(rows, 12, s.reversed_entry_id.name if s.move_type == 'out_refund' else '-', header_data_format)
                    worksheet.write(rows, 13, 0.00, currency_format)
                    worksheet.write(rows, 14, 0.00, currency_format)
                    worksheet.write(rows, 15, 0.00, currency_format)
                    worksheet.write(rows, 16, 0.00, currency_format)
                    worksheet.write(rows, 17, 0.00, currency_format)
                    worksheet.write(rows, 18, 0.00, currency_format)
                    worksheet.write(rows, 19, '', header_data_format)
                    worksheet.write(rows, 20, '', header_data_format)
                    worksheet.write(rows, 21, '', header_data_format)
                    worksheet.write(rows, 22, '', header_data_format)
                    worksheet.write(rows, 23, '', header_data_format)
                    worksheet.write(rows, 24, 0.00, currency_format)

            #linea de las retenciones
            for ret in dict_fact['rete'].sorted(lambda r: (r.retention_id.date, r.retention_id.id)):
                rows += 1            
                cont += 1
                worksheet.write(rows, 0, cont, header_data_format)                                                              #NUM
                worksheet.write_datetime(rows,1, ret.retention_id.date, fecha)                                                  #FECHA RETENCION
                worksheet.write(rows, 2, ret.retention_id.partner_id.rif, header_data_format)                                   #RIF
                worksheet.write(rows, 3, ret.retention_id.partner_id.name, header_data_format)                                  #NOMBRE O RAZON SOCIAL
                worksheet.write(rows, 4, '-', header_data_format)                                                               #NUMERO DE FACTURA
                worksheet.write(rows, 5, '-', header_data_format)                                                               #SERIE
                worksheet.write(rows, 6, ret.invoice_id.nro_control if ret.invoice_id.nro_control else '-', header_data_format) #NRO DE CONTROL
                worksheet.write(rows, 7, '-', header_data_format)                                                               #NRO CREDITO
                worksheet.write(rows, 8, "-", header_merge_format)                                                              #Num de Import
                worksheet.write(rows, 9, "-", header_merge_format)                                                              #Num de expedient                        

                worksheet.write(rows, 10, '-', header_data_format)                                                               #NRO DEBITO
                worksheet.write(rows, 11, '-', header_data_format)                                                               #TIPO TRANSACCION
                worksheet.write(rows, 12, ret.invoice_id.name if ret.invoice_id.name else '-', header_data_format)              #NRO DE FACTURA AFECTADA
                worksheet.write(rows, 13, 0.00, currency_format)                                                                #COMPREA INCLUYENDO IVA
                worksheet.write(rows, 14, 0.00, currency_format)                                                                #EXENTO
                worksheet.write(rows, 15, 0.00, currency_format)                                                                #BASE IMPONIBLE
                worksheet.write(rows, 16, 0.00, currency_format)                                                                #ALIQUOTA
                worksheet.write(rows, 17, 0.00, currency_format)                                                                #IMPUESTO IVA
                worksheet.write(rows, 18, 0.00, currency_format)                                                                #EXENTO
                worksheet.write(rows, 19, '', header_data_format)                                                               #BASE IMPONIBLE
                worksheet.write(rows, 20, '', header_data_format)                                                               #ALIQUOTA
                worksheet.write(rows, 21, '', header_data_format)                                                               #IMPUESTO IVA
                worksheet.write(rows, 22, ret.ret_amount*-1 if ret.retention_id.move_type == 'out_refund' \
                else ret.ret_amount, currency_format)                                                                           #IVA RETENIDO AL COMPRADOR
                worksheet.write(rows, 23, ret.retention_id.customer_doc_number , header_data_format)                            #COMPROBANTE DE RETENCION
                worksheet.write(rows, 24, '-', header_data_format)                                                              #////

            #Calculos Totales
            R46 = R41+R40+R42+R442+R443
            R47 = R43+R452+R453
            R54 = R34

            #TOTALES        
            worksheet.write(rows+1, 12,'TOTALES', header_data_format)
            worksheet.write(rows+1, 13, total, currency_format)                     #Total Ventas Incluyendo el IVA
            worksheet.write(rows+1, 14, acum_exento, currency_format)                       #Ventas Internas No Gravadas
            worksheet.write(rows+1, 15, base_imponible_total, currency_format)      #Base Imponible
            worksheet.write(rows+1, 16, '-', header_data_format)                  #alicuota
            worksheet.write(rows+1, 17, tax, currency_format)                       #Total Impuestos (General + Adicional + Reducido)
            worksheet.write(rows+1, 22, retencion, currency_format)                 #IVA RETENIDO POR EL COMPRADOR
            worksheet.write(rows+1, 23, '-', header_data_format)                  #número de comprobante
            worksheet.write(rows+1, 24, iva_percibido , currency_format)            #IVA PERCIBIDO

            #TABLA ADICIONAL
            #ESTRUCTURA DE LA TABLA
            #COLUMNAS
            worksheet.write(rows+3, 13,'', header_data_format)#1
            worksheet.merge_range(rows+3, 14, rows+3, 15,  'Base imponible', header_data_format) #2
            worksheet.merge_range(rows+3, 16, rows+3, 17,  'Debito Fiscal', header_data_format)  #3
            worksheet.write(rows+3, 18,'', header_data_format) #4
            worksheet.merge_range(rows+3, 19, rows+3, 20,  'IVA Retenido por el Comprador', header_data_format)#5
            worksheet.merge_range(rows+3, 21, rows+3, 22,  'IVA Percibido', header_data_format) #6

            #FILAS
            worksheet.merge_range(rows+4, 7, rows+4, 12,  'Total : Ventas Internas No Gravadas', header_data_format)
            worksheet.merge_range(rows+5, 7, rows+5, 12,  'Total : Ventas de Exportacion', header_data_format  )
            worksheet.merge_range(rows+6, 7, rows+6, 12,  'Total : Ventas Internas Afectas solo Alicuota General', header_data_format)
            worksheet.merge_range(rows+7, 7, rows+7, 12,  'Total : Ventas Internas Afectas en Alicuota General + Adicional', header_data_format)
            worksheet.merge_range(rows+8, 7, rows+8, 12,  'Total : Ventas Internas Afectas en Alicuota Reducida', header_data_format)
            worksheet.merge_range(rows+9, 7, rows+9, 12,  'Total', header_data_format)

            worksheet.write(rows+4, 13,'40', header_data_format)    #1
            worksheet.write(rows+5, 13,'41', header_data_format)
            worksheet.write(rows+6, 13,'42', header_data_format)    #1
            worksheet.write(rows+7, 13,'442', header_data_format)   #1
            worksheet.write(rows+8, 13,'443', header_data_format)   #1
            worksheet.write(rows+9, 13,'46', header_data_format)    #1
            
            worksheet.write(rows+4, 18,'', header_data_format)      #4
            worksheet.write(rows+5, 18,'', header_data_format)
            worksheet.write(rows+6, 18,'43', header_data_format)    #4
            worksheet.write(rows+7, 18,'452', header_data_format)   #4
            worksheet.write(rows+8, 18,'453', header_data_format)   #4
            worksheet.write(rows+9, 18,'47', header_data_format)    #4
            
            #INGRESAMOS LOS DATOS EN LA TABLA
            worksheet.merge_range(rows+4, 14, rows+4, 15, R40 if R40 else 0.00, currency_format)#2
            worksheet.merge_range(rows+5, 14, rows+5, 15, R41 if R41 else 0.00, currency_format )#2
            worksheet.merge_range(rows+6, 14, rows+6, 15, R42 if R42 else 0.00, currency_format)#2
            worksheet.merge_range(rows+7, 14, rows+7, 15, R442 if R442 else 0.00, currency_format)#2
            worksheet.merge_range(rows+8, 14, rows+8, 15, R443 if R443 else 0.00, currency_format)#2
            worksheet.merge_range(rows+9, 14, rows+9, 15, R46 if R46 else 0.00, currency_format)#2
            
            worksheet.merge_range(rows+4, 16, rows+4, 17, '', header_data_format)#3
            worksheet.merge_range(rows+5, 16, rows+5, 17, '', header_data_format )#3
            worksheet.merge_range(rows+6, 16, rows+6, 17, R43 if R43 else 0.00, currency_format)#3
            worksheet.merge_range(rows+7, 16, rows+7, 17, R452 if R452 else 0.00, currency_format)#3
            worksheet.merge_range(rows+8, 16, rows+8, 17, R453 if R453 else 0.00, currency_format)#3
            worksheet.merge_range(rows+9, 16, rows+9, 17, R47 if R47 else 0.00, currency_format)#3

            worksheet.merge_range(rows+4, 19, rows+4, 20, '', header_data_format)#5
            worksheet.merge_range(rows+5, 19, rows+5, 20, '', header_data_format )#5
            worksheet.merge_range(rows+6, 19, rows+6, 20, '', header_data_format)#5
            worksheet.merge_range(rows+7, 19, rows+7, 20, retencion_ga if retencion_ga else 0.00, currency_format)#5
            worksheet.merge_range(rows+8, 19, rows+8, 20, retencion_r if retencion_r else 0.00, currency_format)#5
            worksheet.merge_range(rows+9, 19, rows+9, 20, '', header_data_format)#5

            worksheet.merge_range(rows+4, 21, rows+4, 22,  '', header_data_format) #6
            worksheet.merge_range(rows+5, 21, rows+5, 22, '', header_data_format )#6
            worksheet.merge_range(rows+6, 21, rows+6, 22, '', header_data_format)#6
            worksheet.merge_range(rows+7, 21, rows+7, 22,  iva_percibido_ga if iva_percibido_ga else 0.00, currency_format) #6
            worksheet.merge_range(rows+8, 21, rows+8, 22,  iva_percibido_r if iva_percibido_r else 0.00, currency_format) #6
            worksheet.merge_range(rows+9, 21, rows+9, 22, '', header_data_format) #6

            #ULTIMA TABLA
            #COLUMNAS
            worksheet.merge_range(rows+11, 17, rows+11, 18, 'Contribuyente', header_data_format)
            worksheet.merge_range(rows+12, 17, rows+12, 18, 'No Contribuyente', header_data_format)

            #FILAS
            worksheet.merge_range(rows+10, 19, rows+10, 20, 'Base Imponible', header_data_format)
            worksheet.merge_range(rows+10, 21, rows+10, 22, 'Debito Fiscal', header_data_format)

            #INGRESAMOS LOS DATOS A LA ULTIMA TABLA
            #CONTRIBUYENTE
            worksheet.merge_range(rows+11, 19, rows+11, 20, R42 if R42 else 0.00, currency_format) #base imponible
            worksheet.merge_range(rows+11, 21, rows+11, 22, R43 if R43 else 0.00, currency_format) #debito fiscal

            #NO CONTRIBUYENTE
            worksheet.merge_range(rows+12, 19, rows+12, 20, '', header_data_format) #base imponible
            worksheet.merge_range(rows+12, 21, rows+12, 22, '', header_data_format) #debito fiscal
            
            workbook.close()
            out=base64.encodestring(fp.getvalue())
            self.write({
                'states': 'get',
                'data': out,
                'name': xls_filename
            })
            return {
                'name': 'Libro de Ventas',
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new'
            }
        else:
            dict_fact = self._get_report_values(data)
            facs = dict_fact['fact'].filtered(lambda doc: doc.transaction_type != '04-ajuste')
            base_imponible_total = 0
            total_exentas=0
            for s in facs.filtered('invoice_date').sorted(lambda m: (m.invoice_date, m.name)):
                rows += 1            
                cont += 1
                if s.doc_impor_export:
                    if s.state !='annulled' and s.state !='cancel':
                        if s.retention == '01-sin':
                            retention = 0
                        if s.retention == '02-special':
                            retention = 0.75
                        if s.retention == '03-ordinary':
                            retention = 1

                        # COMIENZAN LOS CALCULOS
                        if s.move_type == 'out_invoice':
                            total = total + (sum(s.mapped('amount_total'))*s.manual_currency_exchange_rate)
                        if s.move_type == 'out_refund':
                            total = total - (sum(s.mapped('amount_total'))*s.manual_currency_exchange_rate)
                        #Calculamos el Exento
                        exento = (sum(s.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                        #IMPUESTOS REDUCIDOS
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced')))):
                            #BASE IMPONIBLE DEL IMPUESTO
                            if s.move_type == 'out_invoice':
                                R41 = R41 + (sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            if s.move_type == 'out_refund':
                                R41 = R41 - (sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
    
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR-->
                                if s.move_type == 'out_refund': 
                                    retencion_r = retencion_r-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice': 
                                    retencion_r = retencion_r+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund':
                                    iva_percibido_r = iva_percibido_r-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice':
                                    iva_percibido_r = iva_percibido_r+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                    
                        #IMPUESTOS ADICIONALES                
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional')))):
                            #Base imponible del Impuesto
                            if s.move_type == 'out_invoice': 
                                R41= R41 +(sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            if s.move_type == 'out_refund': 
                                R41= R41 -(sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            #Monto del Impuesto
        
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR-->
                                if s.move_type == 'out_refund':
                                    retencion_ga = retencion_ga-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice':
                                    retencion_ga =retencion_ga+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund': 
                                    iva_percibido_ga = iva_percibido_ga-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice': 
                                    iva_percibido_ga = iva_percibido_ga+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                        
                        #IMPUESTOS GENERALES
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general')))):
                            #Base imponible del Impuesto
                            if s.move_type == 'out_invoice':
                                R41= R41 +(sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            if s.move_type == 'out_refund':
                                R41= R41 -(sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)

                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                            #IVA RETENIDO POR EL COMPRADOR
                                if s.move_type == 'out_refund':
                                    retencion_g = retencion_g-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice':
                                    retencion_g = retencion_g+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund':
                                    iva_percibido_g = iva_percibido_g-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice':
                                    iva_percibido_g = iva_percibido_g+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))

                        #Calculamos el TOTAL de impuestos EXENTOS
                        if s.move_type == 'out_invoice':
                            untaxed = untaxed + exento
                        if s.move_type == 'out_refund':
                            untaxed = untaxed - exento
                        if s.move_type == 'out_invoice':
                            R41 = R41 + exento
                        if s.move_type == 'out_refund':
                            R41 = R41 - exento
                        #Retenciones
                        if s.move_type == 'out_invoice':
                            retencion = retencion + s.wh_id.total_tax_ret
                        if s.move_type == 'out_refund':
                            retencion = retencion - s.wh_id.total_tax_ret
                        #TOTAL de IMPUESTOS (Reducido + General + Adicional)
                        if s.move_type == 'out_invoice':
                            tax = tax + s.amount_tax
                        if s.move_type == 'out_refund':
                            tax = tax - s.amount_tax
                        #IVA PERCIBIDO
                        if s.move_type == 'out_invoice':
                            iva_percibido = iva_percibido+((s.amount_tax)-(s.wh_id.total_tax_ret))
                        if s.move_type == 'out_refund':
                            iva_percibido = iva_percibido-((s.amount_tax)-(s.wh_id.total_tax_ret))
                        #TERMINAN LOS CALCULOS
                else:
                    if s.state !='annulled' and s.state !='cancel':
                        if s.retention == '01-sin':
                            retention = 0
                        if s.retention == '02-special':
                            retention = 0.75
                        if s.retention == '03-ordinary':
                            retention = 1

                        # COMIENZAN LOS CALCULOS
                        if s.move_type == 'out_invoice':
                            total = total + (sum(s.mapped('amount_total'))*s.manual_currency_exchange_rate)
                        if s.move_type == 'out_refund':
                            total = total - (sum(s.mapped('amount_total'))*s.manual_currency_exchange_rate)
                        #Calculamos el Exento
                        exento = (sum(s.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                        #IMPUESTOS REDUCIDOS
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced')))):
                            #BASE IMPONIBLE DEL IMPUESTO
                            if s.move_type == 'out_invoice':
                                R443 = R443 + (sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            if s.move_type == 'out_refund':
                                R443 = R443 - (sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            #MONTO DEL IMPUESTO
                            if s.move_type == 'out_invoice':
                                R453 = R453 + (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*s.manual_currency_exchange_rate
                            if s.move_type == 'out_refund':
                                R453 = R453 - (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*s.manual_currency_exchange_rate
                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR-->
                                if s.move_type == 'out_refund': 
                                    retencion_r = retencion_r-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice': 
                                    retencion_r = retencion_r+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund':
                                    iva_percibido_r = iva_percibido_r-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice':
                                    iva_percibido_r = iva_percibido_r+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                    
                        #IMPUESTOS ADICIONALES                
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional')))):
                            #Base imponible del Impuesto
                            if s.move_type == 'out_invoice': 
                                R442= R442 +(sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            if s.move_type == 'out_refund': 
                                R442= R442 -(sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            #Monto del Impuesto
                            if s.move_type == 'out_invoice':
                                R452= R452 + (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*s.manual_currency_exchange_rate
                            if s.move_type == 'out_refund':
                                R452= R452 - (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*s.manual_currency_exchange_rate
                        
                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR-->
                                if s.move_type == 'out_refund':
                                    retencion_ga = retencion_ga-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice':
                                    retencion_ga =retencion_ga+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund': 
                                    iva_percibido_ga = iva_percibido_ga-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice': 
                                    iva_percibido_ga = iva_percibido_ga+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                        
                        #IMPUESTOS GENERALES
                        if len(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general')))):
                            #Base imponible del Impuesto
                            if s.move_type == 'out_invoice':
                                R42= R42 +(sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            if s.move_type == 'out_refund':
                                R42= R42 -(sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                            #Monto del Impuesto
                            if s.move_type == 'out_invoice':
                                R43 = R43 + (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*s.manual_currency_exchange_rate
                            if s.move_type == 'out_refund':
                                R43 = R43 - (sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*s.manual_currency_exchange_rate
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if s.wh_id:
                            #IVA RETENIDO POR EL COMPRADOR
                                if s.move_type == 'out_refund':
                                    retencion_g = retencion_g-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                if s.move_type == 'out_invoice':
                                    retencion_g = retencion_g+((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if s.move_type == 'out_refund':
                                    iva_percibido_g = iva_percibido_g-(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))
                                if s.move_type == 'out_invoice':
                                    iva_percibido_g = iva_percibido_g+(sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(s.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))

                        #Calculamos el TOTAL de impuestos EXENTOS
                        if s.move_type == 'out_invoice':
                            untaxed = untaxed + exento
                        if s.move_type == 'out_refund':
                            
                            untaxed = untaxed - exento
                        if s.move_type == 'out_invoice':
                            R40 = R40 + exento
                        if s.move_type == 'out_refund':
                            R40 = R40 - exento
                        #Retenciones
                        if s.move_type == 'out_invoice':
                            retencion = retencion + s.wh_id.total_tax_ret
                        if s.move_type == 'out_refund':
                            retencion = retencion - s.wh_id.total_tax_ret
                        #TOTAL de IMPUESTOS (Reducido + General + Adicional)
                        if s.move_type == 'out_invoice':
                            tax = tax + s.amount_tax
                        if s.move_type == 'out_refund':
                            tax = tax - s.amount_tax
                        #IVA PERCIBIDO
                        if s.move_type == 'out_invoice':
                            iva_percibido = iva_percibido+((s.amount_tax)-(s.wh_id.total_tax_ret))
                        if s.move_type == 'out_refund':
                            iva_percibido = iva_percibido-((s.amount_tax)-(s.wh_id.total_tax_ret))
                        #TERMINAN LOS CALCULOS

                worksheet.write(rows, 0, cont, header_data_format)
                worksheet.write_datetime(rows,1, s.invoice_date, fecha)
                worksheet.write(rows, 2, s.partner_id.rif, header_data_format)
                worksheet.write(rows, 3, s.partner_id.name, header_data_format)
                
                worksheet.write(rows, 4, '-' if s.transaction_type in ('02-complemento','03-anulacion') else int(s.name) if len(s.name) <= 6 else s.name, header_data_format)
                
                worksheet.write(rows, 5, 'Serie '+s.account_serie.upper() if s.account_serie else '-', header_data_format)
                if s.move_type=='out_invoice':
                    worksheet.write(rows, 6, s.nro_control, header_data_format)
                if s.move_type == 'out_refund':
                    worksheet.write(rows, 6, s.ref_credit, header_data_format)
                
                worksheet.write(rows, 7,'-', header_data_format)
                worksheet.write(rows, 8, s.num_import, header_data_format)                       #Número de Planilla de Importación
                worksheet.write(rows, 9, s.num_export, header_data_format)                       #Número de Expediente Importación
                worksheet.write(rows, 10, s.num_credit if s.move_type == 'out_refund' else '-', header_data_format)
                worksheet.write(rows, 11, s.transaction_type, header_data_format)
                worksheet.write(rows, 12, s.reversed_entry_id.name if s.move_type == 'out_refund' else '-', header_data_format)
                worksheet.write(rows, 13, sum(s.mapped('amount_total'))*s.manual_currency_exchange_rate if s.move_type == 'out_refund' else sum(s.mapped('amount_total'))*s.manual_currency_exchange_rate, currency_format)


                monto_impuesto = (sum(s.invoice_line_ids.mapped('tax_ids.amount'))*s.manual_currency_exchange_rate)
                monto_impuesto_untaxed = (sum(s.invoice_line_ids.filtered(lambda whl: not whl.tax_ids).mapped('price_subtotal')) + sum(s.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                monto_impuesto_untaxed_exento = (sum(s.invoice_line_ids.filtered(lambda whl: len(whl.tax_ids) == 0).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                if monto_impuesto == 0 or monto_impuesto_untaxed > 0 or monto_impuesto_untaxed_exento:
                    worksheet.write(rows,14, exento if s.move_type == 'in_refund' else exento, currency_format)
                    acum_exento += (exento)
                else:
                    worksheet.write(rows,14, 0.0, currency_format)
                
                if sum(s.invoice_line_ids.mapped('tax_ids.amount')) > 0:
                    #worksheet.write(rows, 13, sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids) > 0).mapped('price_subtotal')) * -1 if s.move_type == 'out_refund' else sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids) > 0).mapped('price_subtotal')), currency_format)
                    worksheet.write(rows, 15, (sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids.filtered(lambda imp: imp.amount > 0))>0).mapped('price_subtotal'))*s.manual_currency_exchange_rate) if s.move_type == 'out_refund' else (sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids.filtered(lambda imp: imp.amount > 0))>0).mapped('price_subtotal'))*s.manual_currency_exchange_rate), currency_format)

                    #MODIFICADO PARA QUE TOME EN CUENTA LAS NOTAS DE CREDITO Y RESTE
                    if s.move_type == 'out_invoice':
                        base_imponible_total = base_imponible_total + (sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids.filtered(lambda imp: imp.amount >0))>0).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                    if s.move_type == 'out_refund':
                        base_imponible_total = base_imponible_total - (sum(s.invoice_line_ids.filtered(lambda line: len(line.tax_ids.filtered(lambda imp: imp.amount >0))>0).mapped('price_subtotal'))*s.manual_currency_exchange_rate)
                

                else:
                    worksheet.write(rows, 15, 0.00, currency_format)
                worksheet.write(rows, 16, sum(s.invoice_line_ids.mapped('tax_ids.amount')), currency_format)
                worksheet.write(rows, 17, s.amount_tax*s.manual_currency_exchange_rate if s.move_type == 'out_refund' else s.amount_tax *s.manual_currency_exchange_rate, currency_format)
                worksheet.write(rows, 18, '', header_data_format )
                worksheet.write(rows, 19, '', header_data_format)
                worksheet.write(rows, 20, '', header_data_format)
                worksheet.write(rows, 21, '', header_data_format)
                worksheet.write(rows, 22, '', header_data_format)
                worksheet.write(rows, 23, '', header_data_format)
                worksheet.write(rows, 24, ((s.amount_tax)-(s.wh_id.total_tax_ret))*-1 if s.move_type == 'out_refund' else (s.amount_tax)-(s.wh_id.total_tax_ret), currency_format)

                if s.state =='cancel':
                    worksheet.write(rows, 0, cont, header_data_format)
                    worksheet.write_datetime(rows,1, s.invoice_date, fecha)
                    worksheet.write(rows, 2, s.partner_id.rif, header_data_format)
                    worksheet.write(rows, 3, s.partner_id.name, header_data_format)
                    worksheet.write(rows, 4, '-' if s.transaction_type in ('02-complemento','03-anulacion') else int(s.name) if len(s.name) <= 6 else s.name, header_data_format)
                    worksheet.write(rows, 5, 'Serie '+s.account_serie.upper() if s.account_serie else '-', header_data_format)
                    worksheet.write(rows, 6, s.nro_control if s.nro_control else '-', header_data_format)
                    worksheet.write(rows, 7, '-', header_data_format)
                    worksheet.write(rows, 8, '-', header_data_format)
                    worksheet.write(rows, 9, '-', header_data_format)
                    worksheet.write(rows, 10, s.num_credit if s.move_type == 'out_refund' else '-', header_data_format)
                    worksheet.write(rows, 11, s.transaction_type, header_data_format)
                    worksheet.write(rows, 12, s.reversed_entry_id.name if s.move_type == 'out_refund' else '-', header_data_format)
                    worksheet.write(rows, 13, 0.00, currency_format)
                    worksheet.write(rows, 14, 0.00, currency_format)
                    worksheet.write(rows, 15, 0.00, currency_format)
                    worksheet.write(rows, 16, 0.00, currency_format)
                    worksheet.write(rows, 17, 0.00, currency_format)
                    worksheet.write(rows, 18, 0.00, currency_format)
                    worksheet.write(rows, 19, '', header_data_format)
                    worksheet.write(rows, 20, '', header_data_format)
                    worksheet.write(rows, 21, '', header_data_format)
                    worksheet.write(rows, 22, '', header_data_format)
                    worksheet.write(rows, 23, '', header_data_format)
                    worksheet.write(rows, 24, 0.00, currency_format)

            #linea de las retenciones
            for ret in dict_fact['rete'].sorted(lambda r: (r.retention_id.date, r.retention_id.id)):
                rows += 1            
                cont += 1
                worksheet.write(rows, 0, cont, header_data_format)                                                              #NUM
                worksheet.write_datetime(rows,1, ret.retention_id.date, fecha)                                                  #FECHA RETENCION
                worksheet.write(rows, 2, ret.retention_id.partner_id.rif, header_data_format)                                   #RIF
                worksheet.write(rows, 3, ret.retention_id.partner_id.name, header_data_format)                                  #NOMBRE O RAZON SOCIAL
                worksheet.write(rows, 4, '-', header_data_format)                                                               #NUMERO DE FACTURA
                worksheet.write(rows, 5, '-', header_data_format)                                                               #SERIE
                worksheet.write(rows, 6, ret.invoice_id.nro_control if ret.invoice_id.nro_control else '-', header_data_format) #NRO DE CONTROL
                worksheet.write(rows, 7, '-', header_data_format)                                                               #NRO CREDITO
                worksheet.write(rows, 8, "-", header_merge_format)                                                              #Num de Import
                worksheet.write(rows, 9, "-", header_merge_format)                                                              #Num de expedient                        

                worksheet.write(rows, 10, '-', header_data_format)                                                               #NRO DEBITO
                worksheet.write(rows, 11, '-', header_data_format)                                                               #TIPO TRANSACCION
                worksheet.write(rows, 12, ret.invoice_id.name if ret.invoice_id.name else '-', header_data_format)              #NRO DE FACTURA AFECTADA
                worksheet.write(rows, 13, 0.00, currency_format)                                                                #COMPREA INCLUYENDO IVA
                worksheet.write(rows, 14, 0.00, currency_format)                                                                #EXENTO
                worksheet.write(rows, 15, 0.00, currency_format)                                                                #BASE IMPONIBLE
                worksheet.write(rows, 16, 0.00, currency_format)                                                                #ALIQUOTA
                worksheet.write(rows, 17, 0.00, currency_format)                                                                #IMPUESTO IVA
                worksheet.write(rows, 18, 0.00, currency_format)                                                                #EXENTO
                worksheet.write(rows, 19, '', header_data_format)                                                               #BASE IMPONIBLE
                worksheet.write(rows, 20, '', header_data_format)                                                               #ALIQUOTA
                worksheet.write(rows, 21, '', header_data_format)                                                               #IMPUESTO IVA
                worksheet.write(rows, 22, ret.ret_amount*-1 if ret.retention_id.move_type == 'out_refund' \
                else ret.ret_amount, currency_format)                                                                           #IVA RETENIDO AL COMPRADOR
                worksheet.write(rows, 23, ret.retention_id.customer_doc_number , header_data_format)                            #COMPROBANTE DE RETENCION
                worksheet.write(rows, 24, '-', header_data_format)                                                              #////

            #Calculos Totales
            R46 = R41+R40+R42+R442+R443
            R47 = R43+R452+R453
            R54 = R34

            #TOTALES        
            worksheet.write(rows+1, 12,'TOTALES', header_data_format)
            worksheet.write(rows+1, 13, total, currency_format)                     #Total Ventas Incluyendo el IVA
            worksheet.write(rows+1, 14, acum_exento, currency_format)                       #Ventas Internas No Gravadas
            worksheet.write(rows+1, 15, base_imponible_total, currency_format)      #Base Imponible
            worksheet.write(rows+1, 16, '-', header_data_format)                  #alicuota
            worksheet.write(rows+1, 17, tax *s.manual_currency_exchange_rate, currency_format)                       #Total Impuestos (General + Adicional + Reducido)
            worksheet.write(rows+1, 22, retencion, currency_format)                 #IVA RETENIDO POR EL COMPRADOR
            worksheet.write(rows+1, 23, '-', header_data_format)                  #número de comprobante
            worksheet.write(rows+1, 24, iva_percibido , currency_format)            #IVA PERCIBIDO

            #TABLA ADICIONAL
            #ESTRUCTURA DE LA TABLA
            #COLUMNAS
            worksheet.write(rows+3, 13,'', header_data_format)#1
            worksheet.merge_range(rows+3, 14, rows+3, 15,  'Base imponible', header_data_format) #2
            worksheet.merge_range(rows+3, 16, rows+3, 17,  'Debito Fiscal', header_data_format)  #3
            worksheet.write(rows+3, 18,'', header_data_format) #4
            worksheet.merge_range(rows+3, 19, rows+3, 20,  'IVA Retenido por el Comprador', header_data_format)#5
            worksheet.merge_range(rows+3, 21, rows+3, 22,  'IVA Percibido', header_data_format) #6

            #FILAS
            worksheet.merge_range(rows+4, 7, rows+4, 12,  'Total : Ventas Internas No Gravadas', header_data_format)
            worksheet.merge_range(rows+5, 7, rows+5, 12,  'Total : Ventas de Exportacion', header_data_format  )
            worksheet.merge_range(rows+6, 7, rows+6, 12,  'Total : Ventas Internas Afectas solo Alicuota General', header_data_format)
            worksheet.merge_range(rows+7, 7, rows+7, 12,  'Total : Ventas Internas Afectas en Alicuota General + Adicional', header_data_format)
            worksheet.merge_range(rows+8, 7, rows+8, 12,  'Total : Ventas Internas Afectas en Alicuota Reducida', header_data_format)
            worksheet.merge_range(rows+9, 7, rows+9, 12,  'Total', header_data_format)

            worksheet.write(rows+4, 13,'40', header_data_format)    #1
            worksheet.write(rows+5, 13,'41', header_data_format)
            worksheet.write(rows+6, 13,'42', header_data_format)    #1
            worksheet.write(rows+7, 13,'442', header_data_format)   #1
            worksheet.write(rows+8, 13,'443', header_data_format)   #1
            worksheet.write(rows+9, 13,'46', header_data_format)    #1
            
            worksheet.write(rows+4, 18,'', header_data_format)      #4
            worksheet.write(rows+5, 18,'', header_data_format)
            worksheet.write(rows+6, 18,'43', header_data_format)    #4
            worksheet.write(rows+7, 18,'452', header_data_format)   #4
            worksheet.write(rows+8, 18,'453', header_data_format)   #4
            worksheet.write(rows+9, 18,'47', header_data_format)    #4
            
            #INGRESAMOS LOS DATOS EN LA TABLA
            worksheet.merge_range(rows+4, 14, rows+4, 15, R40 if R40 else 0.00, currency_format)#2
            worksheet.merge_range(rows+5, 14, rows+5, 15, R41 if R41 else 0.00, currency_format )#2
            worksheet.merge_range(rows+6, 14, rows+6, 15, R42 if R42 else 0.00, currency_format)#2
            worksheet.merge_range(rows+7, 14, rows+7, 15, R442 if R442 else 0.00, currency_format)#2
            worksheet.merge_range(rows+8, 14, rows+8, 15, R443 if R443 else 0.00, currency_format)#2
            worksheet.merge_range(rows+9, 14, rows+9, 15, R46 if R46 else 0.00, currency_format)#2
            
            worksheet.merge_range(rows+4, 16, rows+4, 17, '', header_data_format)#3
            worksheet.merge_range(rows+5, 16, rows+5, 17, '', header_data_format )#3
            worksheet.merge_range(rows+6, 16, rows+6, 17, R43 if R43 else 0.00, currency_format)#3
            worksheet.merge_range(rows+7, 16, rows+7, 17, R452 if R452 else 0.00, currency_format)#3
            worksheet.merge_range(rows+8, 16, rows+8, 17, R453 if R453 else 0.00, currency_format)#3
            worksheet.merge_range(rows+9, 16, rows+9, 17, R47 if R47 else 0.00, currency_format)#3

            worksheet.merge_range(rows+4, 19, rows+4, 20, '', header_data_format)#5
            worksheet.merge_range(rows+5, 19, rows+5, 20, '', header_data_format )#5
            worksheet.merge_range(rows+6, 19, rows+6, 20, '', header_data_format)#5
            worksheet.merge_range(rows+7, 19, rows+7, 20, retencion_ga if retencion_ga else 0.00, currency_format)#5
            worksheet.merge_range(rows+8, 19, rows+8, 20, retencion_r if retencion_r else 0.00, currency_format)#5
            worksheet.merge_range(rows+9, 19, rows+9, 20, '', header_data_format)#5

            worksheet.merge_range(rows+4, 21, rows+4, 22,  '', header_data_format) #6
            worksheet.merge_range(rows+5, 21, rows+5, 22, '', header_data_format )#6
            worksheet.merge_range(rows+6, 21, rows+6, 22, '', header_data_format)#6
            worksheet.merge_range(rows+7, 21, rows+7, 22,  iva_percibido_ga if iva_percibido_ga else 0.00, currency_format) #6
            worksheet.merge_range(rows+8, 21, rows+8, 22,  iva_percibido_r if iva_percibido_r else 0.00, currency_format) #6
            worksheet.merge_range(rows+9, 21, rows+9, 22, '', header_data_format) #6

            #ULTIMA TABLA
            #COLUMNAS
            worksheet.merge_range(rows+11, 17, rows+11, 18, 'Contribuyente', header_data_format)
            worksheet.merge_range(rows+12, 17, rows+12, 18, 'No Contribuyente', header_data_format)

            #FILAS
            worksheet.merge_range(rows+10, 19, rows+10, 20, 'Base Imponible', header_data_format)
            worksheet.merge_range(rows+10, 21, rows+10, 22, 'Debito Fiscal', header_data_format)

            #INGRESAMOS LOS DATOS A LA ULTIMA TABLA
            #CONTRIBUYENTE
            worksheet.merge_range(rows+11, 19, rows+11, 20, R42 if R42 else 0.00, currency_format) #base imponible
            worksheet.merge_range(rows+11, 21, rows+11, 22, R43 if R43 else 0.00, currency_format) #debito fiscal

            #NO CONTRIBUYENTE
            worksheet.merge_range(rows+12, 19, rows+12, 20, '', header_data_format) #base imponible
            worksheet.merge_range(rows+12, 21, rows+12, 22, '', header_data_format) #debito fiscal
            
            workbook.close()
            out=base64.encodestring(fp.getvalue())
            self.write({
                'states': 'get',
                'data': out,
                'name': xls_filename
            })
            return {
                'name': 'Libro de Ventas',
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new'
            }
            
