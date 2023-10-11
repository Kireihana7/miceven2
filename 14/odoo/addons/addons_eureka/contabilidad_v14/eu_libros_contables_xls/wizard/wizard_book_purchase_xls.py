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


class WizardBookPurchaseXls(models.TransientModel):
    _name = "wizard.book.purchase.xls"
    _description = 'Libro de Compras Excel'

    name = fields.Char(string='Nombre del Archivo', readonly=True)
    data = fields.Binary(string='Archivo', readonly=True)    

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env.user.company_id)
    journal_ids = fields.Many2many('account.journal', string='Journals',
                                   required=True,
                                   default=lambda self: self.env[
                                       'account.journal'].search([('type', '=','purchase')]))
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries')], string='Target Moves', required=True,
                                   default='posted')
    account_ids = fields.Many2many('account.account',
                                   'account_report_purchase_account_rel_3',
                                   'report_id', 'account_id',
                                   'Accounts')
    date_from = fields.Date(string='Start Date', default=date.today())
    date_to = fields.Date(string='End Date', default=date.today())
    display_account = fields.Selection(
        [('all', 'All'), ('movement', 'With movements'),
         ('not_zero', 'With balance is not equal to 0')],
        string='Display Accounts', required=True, default='movement')
    sortby = fields.Selection(
        [('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')],
        string='Sort by',
        required=True, default='sort_date')
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    states = fields.Selection([
        ('choose', 'choose'), 
        ('get', 'get')], 
        default='choose')
    in_bs = fields.Boolean(string="Mostrar en Bs",default=True)    

    #def _domain_branch_ids(self):
    #    return [('id','in',(self.env.user.branch_ids.ids))]
    #branch_ids = fields.Many2many('res.branch', string='Sucursales',
    #                               required=True,
    #                               default=lambda self: self.env.user.branch_ids,domain=_domain_branch_ids)

    @api.model
    def default_get(self, default_fields):
        vals = super(WizardBookPurchaseXls, self).default_get(default_fields)
        vals['states'] = 'choose'
        return vals

    def go_back(self):
        self.states = 'choose'
        return {
            'name': 'Libro de Compras Excel',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        #result['branch_ids'] = 'branch_ids' in data['form'] and data['form']['branch_ids'] or False
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        result['currency_id'] = data['form']['currency_id'] or False
        result['company_id'] = 'company_id' in data['form'] and data['form']['company_id'] or False
        result['in_bs'] = data['form']['in_bs'] or False
        return result

    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = \
        self.read(['date_from', 'date_to', 'journal_ids', 'target_move','display_account','account_ids','sortby','currency_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context,lang=self.env.context.get('lang') or 'es_ES')
        return self.env.ref('l10n_ve_accountant.shooppin_book').report_action(self,data=data)

    @api.constrains('date_from','date_to')
    def _check_date(self):
        '''
        This method validated that the final date is not less than the initial date
        :return:
        '''
        if self.date_to < self.date_from:
            raise UserError(_("The end date cannot be less than the start date "))

    def _get_account_move_entry(self, accounts, form_data, sortby, pass_date, display_account):
        cr = self.env.cr
        move_line = self.env['account.move.line']

        tables, where_clause, where_params = move_line._query_get()
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
                WHERE l.account_id IN %s AND l.journal_id IN %s ''' + target_move + ''' AND l.date = %s
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
        form_data = data['form']
        #branch_ids = form_data['branch_ids']
        date_start = datetime.datetime.strptime(str(form_data['date_from']), '%Y-%m-%d')
        date_end = datetime.datetime.strptime(str(form_data['date_to']), '%Y-%m-%d')
        
        date_start = fields.Datetime.context_timestamp(self,date_start)
        
        
        target_mov = ('posted',) if form_data['target_move'] =='posted' else ('draft','cancel','posted')
        currency_id = self.env['res.currency'].browse([form_data['currency_id'][0]])
        company_id = self.env.company
        active_acc = data['form']['account_ids']
        accounts = self.env['account.account'].search(
            [('id', 'in', active_acc)]) if data['form']['account_ids'] else \
            self.env['account.account'].search([])
        print('hacker clara')
        print('hacker clara')
        print('hacker clara')
        print(accounts)

        #if not data.get('form') or not self.env.context.get('active_model'):
        #    raise UserError(_("Form content is missing, this report cannot be printed."))

        in_bs = data['form'].get('in_bs')
        sortby = data['form'].get('sortby')
        #las retenciones
        docs_ret = self.env['account.wh.iva'].search([('move_type', 'in', ('in_invoice', 'in_refund'))])
        #las facturas in_invoice y las facturas rectificativas in_refund
        docs_fac = self.env['account.move'].search([('move_type', 'in', ('in_refund', 'in_invoice')),
                                                    ('date','<=',self.date_to),
                                                    ('date','>',date_start),
                                                    #('branch_id', 'in', (branch_ids)),
                                                    ('journal_id','in',form_data['journal_ids']),
                                                    ('state','in', target_mov)]).sorted(
            key=lambda r: r.journal_id.id and r.partner_id.name if sortby=='sort_journal_partner' else r.date).filtered(lambda x: x.line_ids.mapped('account_id') and accounts != self.env['account.account'])
       
        docs_fac_ajust = self.env['account.move'].search([('move_type', 'in', ('in_refund', 'in_invoice')),
                                                    ('ajust_date','<=',self.date_to),
                                                    ('ajust_date','>',date_start),
                                                    ('transaction_type', '=', '04-ajuste'),
                                                    ('currency_id', '=', currency_id.id),
                                                    ('journal_id','in',form_data['journal_ids'])]).sorted(
            key=lambda r: r.journal_id.id and r.partner_id.name if sortby=='sort_journal_partner' else r.date).filtered(lambda x: x.line_ids.mapped('account_id') and accounts != self.env['account.account'])
        rete = self.env['account.wh.iva.line'].search([
                                        ('retention_id.date', '>', date_start),
                                        ('retention_id.date', '<=', self.date_to),
                                        ('retention_id.move_type', 'in', ('in_invoice','in_refund')),
                                        ('state', 'not in', ('draft','cancel','anulled')),
                                        ('retention_id.company_id','=',self.env.company.id),
                                        ])
        if not docs_fac and not rete:
            raise UserError('No se encontraron registros con estas características durante el periodo seleccionado. Verifique los datos ingresados')
        #model = self.env.context.get('active_model')
        display_account = 'movement'
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]
        
        #branch = []
        #if branch_ids:
        #    branch = [branch.name for branch in
        #             self.env['res.branch'].search(
        #                 [('id', 'in', branch_ids)])]                 

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
        print('data')
        print(data)
        return {
            #'doc_ids': docids,
            #'doc_model': model,
            'data': data['form'],
            'docs': docs_ret,
            'fact': docs_fac,
            'rete': rete,
            'docs_fac_ajust': docs_fac_ajust,
            'time': time,
            'hora_printer': hora_printer,
            'Accounts': record,
            'print_journal': codes,
            #'branch': branch,
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
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context,lang=self.env.context.get('lang') or 'es_ES')

        
        #branch_name= self.branch_ids.mapped("name")


        
        xls_filename = 'libro_compras.xlsx'
        fp = BytesIO()
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

        worksheet = workbook.add_worksheet('Libro de Compras Xlsx')

        worksheet.merge_range(0, 1, 1, 4, self.company_id.name, header_data_format_titulo)
        worksheet.merge_range(0, 6, 0, 7, 'Fecha de Impresión:', header_merge_format)
        worksheet.write_datetime(0,8, fields.Datetime.now(), fecha)
    

        worksheet.set_column('A:B', 18)
        worksheet.set_column('C:I', 12)
      
        worksheet.merge_range('F4:H4', ", ", header_merge_format)
        worksheet.merge_range(4, 3, 6, 10,  'LIBRO DE COMPRAS', header_merge_format)
        worksheet.write(8, 5, "Desde:", header_merge_format)
        worksheet.write(8, 6, data['form']['date_from'], fecha)
        worksheet.write(8, 7, "Hasta: ", header_merge_format)
        worksheet.write(8, 8, data['form']['date_to'], fecha)

        worksheet.merge_range(9, 12, 9, 21, 'COMPRAS INTERNAS O IMPORTACIONES', header_merge_format)
        
        worksheet.write(10, 0, "Oper. N°", header_merge_format)
        worksheet.write(10, 1, "Fecha de la Factura", header_merge_format)
        worksheet.write(10, 2, "RIF o Cedula", header_merge_format)
        worksheet.write(10, 3, "Nombre o Razón Social", header_merge_format)
        worksheet.write(10, 4, "Serie", header_merge_format)
        worksheet.write(10, 5, "Tipo de Prov.", header_merge_format)
        worksheet.write(10, 6, "Numero de Factura", header_merge_format)
        worksheet.write(10, 7, "Núm. Control", header_merge_format)
        worksheet.write(10, 8, "Número Planilla de Importación", header_merge_format)
        worksheet.write(10, 9, "Número de Expediente Importación", header_merge_format)
        worksheet.write(10, 10, "Número nota de débito", header_merge_format)
        worksheet.write(10, 11, "Número nota de credito", header_merge_format)
        worksheet.write(10, 12, "Número factura afectada", header_merge_format)
        worksheet.write(10, 13, "Total Compras Incluyendo IVA", header_merge_format)
        worksheet.write(10, 14, "Compras exentas", header_merge_format)
        worksheet.write(10, 15, "Compras Exoneradas", header_merge_format)#exoneradas
        worksheet.write(10, 16, "Compras No sujetas", header_merge_format)#no sujetas
        worksheet.write(10, 17, "Base Imponible", header_merge_format)
        worksheet.write(10, 18, "% Alícuota", header_merge_format)
        worksheet.write(10, 19, "Impuesto IVA Deducible", header_merge_format)
        worksheet.write(10, 20, "Base Imponible no deducible", header_merge_format)
        worksheet.write(10, 21, "% Alícuota", header_merge_format)
        worksheet.write(10, 22, "IVA no deducible", header_merge_format)
        worksheet.write(10, 23, "IVA retenido (al Vendedor)", header_merge_format)
        worksheet.write(10, 24, "% Retención", header_merge_format)
        worksheet.write(10, 25, "Comprobante. de Retención", header_merge_format)

        R30 = 0
        R31 = 0
        R32 = 0
        R312 = 0
        R313 = 0
        R322 = 0
        R323 = 0
        R332 = 0
        R342 = 0
        R333 = 0
        R343 = 0
        R33 = 0
        R34 = 0
        R35 = 0
        R36 = 0
        untaxed = 0
        acum_exento = 0
        untaxed_deductible = 0
        untaxed_not_deductible = 0
        tax = 0
        tax_deductible = 0
        tax_not_deductible = 0
        retencion = 0
        retention = 0
        retencion_three = 0
        total = 0
        iva_percibido = 0
        iva_percibido_g = 0
        retencion_g = 0
        retencion_ga = 0
        iva_percibido_ga = 0
        retencion_r = 0
        iva_percibido_r = 0
        monto_impuesto_untaxed_exento = 0
        prorratas = 0
        porc_prorrata = 0
        acumret = 0
        total_dedu = 0

        rows = 10
        cont = 0
        if not data['form']['in_bs']:
            dict_fact = self._get_report_values(data)
            facs = dict_fact['fact'].filtered(lambda doc: doc.transaction_type != '04-ajuste')
    
            for u in facs.sorted(lambda m: m.invoice_date):
                rows += 1
                cont += 1
                if u.doc_impor_export:

                    if u.state !='annulled':
                        #EMPIEZAN LOS CALCULOS
                        if u.move_type == 'in_invoice':
                            total += sum(u.mapped('amount_total'))
                        if u.move_type == 'in_refund':
                            total -= sum(u.mapped('amount_total'))
                        #Calculamos el Exento
                        
                        exento = sum(u.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal')) 
                        
                        #Calculamos los impuestos REDUCIDOS
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice': 
                                R313 += sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))
                            if u.move_type == 'in_refund':
                                R313 -= sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R323 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))
                            if u.move_type == 'in_refund':
                                R323 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))

                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_r -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_r += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if u.move_type == 'in_refund':
                                    iva_percibido_r -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_r += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))

                        #Calculamos los impuestos ADICIONAL
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice':
                                R312 += sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))
                            if u.move_type == 'in_refund':
                                R312 -= sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R322 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))
                            if u.move_type == 'in_refund':
                                R322 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))
                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_ga -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_ga += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido  -->
                                if u.move_type == 'in_refund':
                                    iva_percibido_ga -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_ga += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))

                        #Calculamos los impuestos GENERAL
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice':
                                R31 += sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))
                            if u.move_type == 'in_refund':
                                R31 -= sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R32 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))
                            if u.move_type == 'in_refund':
                                R32 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_g -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_g += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if u.move_type == 'in_refund':
                                    iva_percibido_g -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_g += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))

                        #Calculamos el TOTAL de impuestos EXENTOS
                        if u.move_type == 'in_invoice':
                            untaxed += exento
                        if u.move_type == 'in_refund':
                            untaxed -= exento
                        if u.move_type == 'in_invoice':
                            R30 += exento
                        if u.move_type == 'in_refund':
                            R30 -= exento
                        #Retenciones
                        if u.move_type == 'in_invoice':
                            retencion += u.wh_id.total_tax_ret
                        if u.move_type == 'in_refund':
                            retencion -= u.wh_id.total_tax_ret
                        #TOTAL de IMPUESTOS (Reducido + General + Adicional)
                        if u.move_type == 'in_invoice':
                            tax += u.amount_tax
                        if u.move_type == 'in_refund':
                            tax -= u.amount_tax
                        #IVA PERCIBIDO
                        if u.move_type == 'in_invoice': 
                            iva_percibido += ((u.amount_tax)-(u.wh_id.total_tax_ret))
                        if u.move_type == 'in_refund':
                            iva_percibido -= ((u.amount_tax)-(u.wh_id.total_tax_ret))
                        #TERMINAN LOS CALCULOS
                    
                else:
                    if u.state !='annulled':
                        #EMPIEZAN LOS CALCULOS
                        if u.move_type == 'in_invoice':
                            total += sum(u.mapped('amount_total'))
                        if u.move_type == 'in_refund':
                            total -= sum(u.mapped('amount_total'))
            
                        #Calculamos el Exento
                        exento = sum(u.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal')) 
                        #Calculamos los impuestos REDUCIDOS
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice': 
                                R333 += sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))
                            if u.move_type == 'in_refund':
                                R333 -= sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R343 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))
                            if u.move_type == 'in_refund':
                                R343 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))

                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_r -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_r += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if u.move_type == 'in_refund':
                                    iva_percibido_r -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_r += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))

                        #Calculamos los impuestos ADICIONAL
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice':
                                R332 += sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))
                            if u.move_type == 'in_refund':
                                R332 -= sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R342 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))
                            if u.move_type == 'in_refund':
                                R342 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))
                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_ga -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_ga += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido  -->
                                if u.move_type == 'in_refund':
                                    iva_percibido_ga -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_ga += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))

                        #Calculamos los impuestos GENERAL
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice':
                                R33 += sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))
                            if u.move_type == 'in_refund':
                                R33 -= sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R34 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))
                            if u.move_type == 'in_refund':
                                R34 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_g -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_g += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if u.move_type == 'in_refund':
                                    iva_percibido_g -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_g += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))

                        #Calculamos el TOTAL de impuestos EXENTOS
                        if u.move_type == 'in_invoice':
                            untaxed += exento
                        if u.move_type == 'in_refund':
                            untaxed -= exento
                        if u.move_type == 'in_invoice':
                            R30 += exento
                        if u.move_type == 'in_refund':
                            R30 -= exento
                        #Retenciones
                        if u.move_type == 'in_invoice':
                            retencion += u.wh_id.total_tax_ret
                        if u.move_type == 'in_refund':
                            retencion -= u.wh_id.total_tax_ret
                        #TOTAL de IMPUESTOS (Reducido + General + Adicional)
                        if u.move_type == 'in_invoice':
                            tax += u.amount_tax
                        if u.move_type == 'in_refund':
                            tax -= u.amount_tax
                        #IVA PERCIBIDO
                        if u.move_type == 'in_invoice': 
                            iva_percibido += ((u.amount_tax)-(u.wh_id.total_tax_ret))
                        if u.move_type == 'in_refund':
                            iva_percibido -= ((u.amount_tax)-(u.wh_id.total_tax_ret))
                    #TERMINAN LOS CALCULOS
        
           
                worksheet.write(rows, 0, cont, header_data_format)
                worksheet.write_datetime(rows,1, u.invoice_date, fecha)
                worksheet.write(rows,2, u.partner_id.rif, header_data_format)
                worksheet.write(rows,3, u.partner_id.name, header_data_format)
                worksheet.write(rows,4, '-', header_data_format) #serie
                worksheet.write(rows,5, u.partner_id.residence_type, header_data_format) #tipo de proveedor
                worksheet.write(rows,6, u.vendor_invoice_number, header_data_format)
                worksheet.write(rows,7, u.nro_control, header_data_format)#Número de Control de Factura
                worksheet.write(rows,8, u.num_import, header_data_format)#Número de Planilla de Importación
                worksheet.write(rows,9, u.num_export, header_data_format)#Número de Expediente Importación
                worksheet.write(rows,10, '-', header_data_format)#Número Nota de Débito
                worksheet.write(rows,11, u.vendor_invoice_number if u.move_type == 'in_refund' else '-', header_data_format)#Número Nota de Crédito
                worksheet.write(rows,12, u.mapped('reversed_entry_id').ref if u.move_type == 'in_refund' else '-', header_data_format)
                worksheet.write(rows,13, sum(u.mapped('amount_total'))*-1 if u.move_type == 'in_refund' else sum(u.mapped('amount_total')), currency_format)
                #Total Compras Incluyendo el IVA                
                monto_impuesto = sum(u.invoice_line_ids.mapped('tax_ids.amount'))
                monto_impuesto_untaxed = sum(u.invoice_line_ids.filtered(lambda whl: not whl.tax_ids).mapped('price_subtotal')) + sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))
                monto_impuesto_untaxed_exento = sum(u.invoice_line_ids.filtered(lambda whl: len(whl.tax_ids) == 0).mapped('price_subtotal'))
                
                if monto_impuesto == 0 or monto_impuesto_untaxed > 0 or monto_impuesto_untaxed_exento:
                    worksheet.write(rows,14, exento*-1 if u.move_type == 'in_refund' else exento, currency_format)
                    acum_exento += (exento)
                else:
                    worksheet.write(rows,14, 0.0, currency_format)
                
                worksheet.write(rows,15, '-', header_data_format)#exoneradas
                worksheet.write(rows,16, '-', header_data_format)#no sujetas
                
                
                #IVA NO DEDUCIBLE
                if not u.deductible:
                    if u.move_type == 'in_invoice':
                        tax_deductible += u.amount_tax
                    if u.move_type == 'in_refund':
                        tax_deductible -= u.amount_tax
                    if u.move_type == 'in_invoice':
                        untaxed_deductible += sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal'))
                    if u.move_type == 'in_refund':
                        untaxed_deductible -= sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal'))
                    if sum(u.invoice_line_ids.mapped('tax_ids.amount')) > 0:
                        worksheet.write(rows,17, (sum(u.mapped('amount_total')) - (exento + u.amount_tax))*-1 if u.move_type == 'in_refund' else sum(u.mapped('amount_total')) - (exento + u.amount_tax), currency_format)
                    else:
                        worksheet.write(rows,17, 0.0, currency_format)
                    
                    worksheet.write(rows,18, sum(u.invoice_line_ids.mapped('tax_ids.amount')), currency_format)#Porcentaje Alicuota
                    worksheet.write(rows,19, u.amount_tax*-1 if u.move_type == 'in_refund' else u.amount_tax, currency_format)
                    worksheet.write(rows,20, '-', header_data_format)
                    worksheet.write(rows,21, '-', header_data_format)
                    worksheet.write(rows,22, '-', header_data_format)

                #Compras Exentas
                if u.deductible:
                    if u.move_type == 'in_invoice':
                        tax_not_deductible += u.amount_tax
                    if u.move_type == 'in_refund':
                        tax_not_deductible -= u.amount_tax
                    if u.move_type == 'in_invoice':
                        untaxed_not_deductible += sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal'))
                    if u.move_type == 'in_refund':
                        untaxed_not_deductible -= sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal'))
                    
                    worksheet.write(rows,17, '-', header_data_format)
                    worksheet.write(rows,18, '-', header_data_format)
                    worksheet.write(rows,19, '-', header_data_format)
                    
                    worksheet.write(rows,20, sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal'))*-1 if u.move_type == 'in_refund' else sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal')), currency_format)
                    worksheet.write(rows,21, sum(u.invoice_line_ids.mapped('tax_ids.amount')), currency_format)
                    worksheet.write(rows,22, u.amount_tax*-1 if u.move_type == 'in_refund' else u.amount_tax, currency_format)

                #Monto Impuesto
                worksheet.write(rows,23, '', currency_format)
                
                #IVA  Retenido al VENDEDOR -->
                worksheet.write(rows,24, '', currency_format)#porcentaje ret
                
                #IVA RETENIDO a Terceros
                worksheet.write(rows,25, '', currency_format)#Prorrata
                    
                #linea de las retenciones
            for ret in dict_fact['rete'].sorted(lambda r: (r.retention_id.date, r.retention_id.id)):
                rows += 1
                cont += 1
                worksheet.write(rows, 0, cont, header_data_format)
                worksheet.write_datetime(rows,1, ret.retention_id.date, fecha)#Fecha de la retención
                worksheet.write(rows,2, ret.retention_id.partner_id.rif, header_data_format)#RIF
                worksheet.write(rows,3, ret.retention_id.partner_id.name, header_data_format)#Nombre o Razón social
                worksheet.write(rows,4, '-',header_data_format)
                worksheet.write(rows,5, ret.retention_id.partner_id.residence_type, header_data_format)#Tipo de Proveedor
                worksheet.write(rows,6, '-', header_data_format)#nmero de factura
                worksheet.write(rows,7, ret.invoice_id.nro_control, header_data_format)#Número de Control de Factura
                worksheet.write(rows,8, '-', header_data_format)#Número de Planilla de Importación
                worksheet.write(rows,9, '-', header_data_format)#Número de Expediente Importación
                worksheet.write(rows,10, '-', header_data_format)#Número Nota de Débito
                worksheet.write(rows,11, '-', header_data_format)#Número Nota de Crédito
                worksheet.write(rows,12, ret.invoice_id.vendor_invoice_number, header_data_format)#numero de factura afectada
                worksheet.write(rows,13, '-', header_data_format)#t compras inclydo iva
                worksheet.write(rows,14, '-', header_data_format)#exento
                worksheet.write(rows,15, '-', header_data_format)#exoneradas
                worksheet.write(rows,16, '-', header_data_format)#no sujetas
                worksheet.write(rows,17, '-', header_data_format)#base imponible
                worksheet.write(rows,18, '-', header_data_format)#aliq
                worksheet.write(rows,19, '-', header_data_format)#imp. iva
                worksheet.write(rows,20, '-', header_data_format)#base imp
                worksheet.write(rows,21, '-', header_data_format)#aliq
                worksheet.write(rows,22, '-', header_data_format)#imp iva
                worksheet.write(rows,23, ret.ret_amount*-1 if ret.retention_id.move_type == 'in_refund' else ret.ret_amount, currency_format)#iva retenido al vendedor
                acumret += ret.ret_amount
                worksheet.write(rows,24, ret.rate_amount*-1 if ret.retention_id.move_type == 'in_refund' else ret.rate_amount, currency_format)#porcentaje ret
                worksheet.write(rows,25, ret.retention_id.number if ret.retention_id.move_type == 'in_refund' else ret.retention_id.number, currency_format)#comprobante de retencion

            worksheet.write(rows+1,13, total, currency_format)
            worksheet.write(rows+1,14, acum_exento, currency_format)
            worksheet.write(rows+1,15, 0.0, currency_format)
            worksheet.write(rows+1,16, 0.0, currency_format)                         
            #DEDUCIBLE INICIO
            worksheet.write(rows+1,17, R33 + R31 + R312 + R313 + R332 + R333, currency_format)
            worksheet.write(rows+1,18, 0.0, currency_format)
            worksheet.write(rows+1,19, tax_deductible, currency_format)
            #DEDUCIBLE FIN
            R30 = acum_exento
            #NO DEDUCIBLE INICIO
            worksheet.write(rows+1,20, untaxed_not_deductible, currency_format)
            worksheet.write(rows+1,21, 0.0, currency_format)
            worksheet.write(rows+1,22, tax_not_deductible, currency_format)
            #MO DEDUCIBLE FIN
            # R34 = tax
            worksheet.write(rows+1,23, retencion, currency_format)
            worksheet.write(rows+1,24, '-', currency_format)

            #Se definen las variables dependientes de otras
            # R34 =R34-R342-R343
            # R342 =R342-R322
            # R343 =R343-R323
            R35 =R30+R332+R333+R33+R312+R313+R31
            R36 =R34+R342+R343+R32+R322+R323

            #TABLA ADICIONAL
            #ESTRUCTURA DE LA TABLA
            #COLUMNAS
            worksheet.write(rows+3, 18,'', header_data_format)#1
            worksheet.merge_range(rows+3, 19, rows+3, 20,  'Base imponible', header_data_format) #2
            worksheet.write(rows+3, 21,'', header_data_format) #3
            worksheet.merge_range(rows+3, 22, rows+3, 23,  'Crédito Fiscal', header_data_format)  #4
            worksheet.merge_range(rows+3, 24, rows+3, 25,  'IVA Retenido (al Vendedor)', header_data_format)#5

            #FILAS
            worksheet.merge_range(rows+4, 12, rows+4, 17,  'Total : Compras Excentas y/o sin derecho a crédito fiscal', header_data_format)
            worksheet.merge_range(rows+5, 12, rows+5, 17,  'Compras Importación afectadas solo Alicuota General', header_data_format)
            worksheet.merge_range(rows+6, 12, rows+6, 17,  'Compras Importación Afectas en Alicuota General + Adicional', header_data_format)
            worksheet.merge_range(rows+7, 12, rows+7, 17,  'Compras Importación Afectas en Alicuota Reducida', header_data_format)
            worksheet.merge_range(rows+8, 12, rows+8, 17,  'Compras Internas Afectas en Alicuota General + Adicional', header_data_format)
            worksheet.merge_range(rows+9, 12, rows+9, 17,  'Compras Internas Afectas en Alicuota Reducida', header_data_format)
            worksheet.merge_range(rows+10, 12, rows+10, 17,'Compras Internas Afectas solo Alicuota General', header_data_format)
            worksheet.merge_range(rows+11, 12, rows+11, 17,'TOTAL', header_data_format)

            worksheet.write(rows+4, 18,'30', header_data_format)                        #1
            worksheet.write(rows+5, 18,'31', header_data_format)                        #1
            worksheet.write(rows+6, 18,'312', header_data_format)                       #1
            worksheet.write(rows+7, 18,'313', header_data_format)                       #1
            worksheet.write(rows+8, 18,'332', header_data_format)                       #1
            worksheet.write(rows+9, 18,'333', header_data_format)                       #1
            worksheet.write(rows+10, 18,'33', header_data_format)                       #1
            worksheet.write(rows+11, 18,'35', header_data_format)                       #1

            worksheet.write(rows+4,  21,'', header_data_format)                         #3
            worksheet.write(rows+5,  21,'32', header_data_format)                       #3
            worksheet.write(rows+6,  21,'322', header_data_format)                      #3
            worksheet.write(rows+7,  21,'323', header_data_format)                      #3
            worksheet.write(rows+8,  21,'342', header_data_format)                      #3
            worksheet.write(rows+9,  21,'343', header_data_format)                      #3
            worksheet.write(rows+10, 21,'34', header_data_format)                       #3
            worksheet.write(rows+11, 21,'36', header_data_format)                       #3

            worksheet.merge_range(rows+4, 19, rows+4, 20,  R30, currency_format)        #2
            worksheet.merge_range(rows+5, 19, rows+5, 20,  R31, currency_format)        #2
            worksheet.merge_range(rows+6, 19, rows+6, 20,  R312, currency_format)       #2
            worksheet.merge_range(rows+7, 19, rows+7, 20,  R313, currency_format)       #2
            worksheet.merge_range(rows+8, 19, rows+8, 20,  R332, currency_format)       #2
            worksheet.merge_range(rows+9, 19, rows+9, 20,  R333, currency_format)       #2
            worksheet.merge_range(rows+10, 19, rows+10, 20,  R33, currency_format)      #2
            worksheet.merge_range(rows+11, 19, rows+11, 20,  R35, currency_format)      #2

            worksheet.merge_range(rows+4, 22, rows+4, 23,  0.0, currency_format)        #4
            worksheet.merge_range(rows+5, 22, rows+5, 23,  R32, currency_format)        #4
            worksheet.merge_range(rows+6, 22, rows+6, 23,  R322, currency_format)       #4
            worksheet.merge_range(rows+7, 22, rows+7, 23,  R323, currency_format)       #4
            worksheet.merge_range(rows+8, 22, rows+8, 23,  R342, currency_format)       #4
            worksheet.merge_range(rows+9, 22, rows+9, 23,  R343, currency_format)       #4
            worksheet.merge_range(rows+10, 22, rows+10, 23, R34, currency_format)      #4
            worksheet.merge_range(rows+11, 22, rows+11, 23, R36, currency_format)      #4

            worksheet.merge_range(rows+4, 24, rows+4, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+5, 24, rows+5, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+6, 24, rows+6, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+7, 24, rows+7, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+8, 24, rows+8, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+9, 24, rows+9, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+10, 24, rows+10, 25,  acumret, currency_format)  #5
            worksheet.merge_range(rows+11, 24, rows+11, 25,  acumret, currency_format)  #5

            #ULTIMA TABLA
            #COLUMNAS

            worksheet.merge_range(rows+13, 21, rows+13, 25, 'Resumen Tasa General', header_data_format)
            worksheet.write(rows+14,  21,'Tasa', header_data_format)
            worksheet.merge_range(rows+14, 22, rows+14, 23, 'Base Imponible', header_data_format)
            worksheet.merge_range(rows+14, 24, rows+14, 25, 'Debito Fiscal', header_data_format)

            worksheet.write(rows+15,  21,'16%', header_data_format)
            worksheet.merge_range(rows+15, 22, rows+15, 23, R33 if R33 else 0.0, currency_format)
            worksheet.merge_range(rows+15, 24, rows+15, 25, R34 if R34 else 0.0, currency_format)
            
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
        else:
            dict_fact = self._get_report_values(data)
            facs = dict_fact['fact'].filtered(lambda doc: doc.transaction_type != '04-ajuste')
    
            for u in facs.sorted(lambda m: m.invoice_date):
                rows += 1
                cont += 1
                if u.doc_impor_export:
                    if u.state !='annulled':
                        #EMPIEZAN LOS CALCULOS
                        if u.move_type == 'in_invoice':
                            total += (sum(u.mapped('amount_total'))*u.manual_currency_exchange_rate)
                        if u.move_type == 'in_refund':
                            total -= (sum(u.mapped('amount_total'))*u.manual_currency_exchange_rate)
                        #Calculamos el Exento
                        
                        exento = (sum(u.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                        
                        #Calculamos los impuestos REDUCIDOS
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice': 
                                R313 += (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            if u.move_type == 'in_refund':
                                R313 -= (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                        
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R323 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            if u.move_type == 'in_refund':
                                R323 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate

                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_r -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_r += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if u.move_type == 'in_refund':
                                    iva_percibido_r -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_r += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))

                        #Calculamos los impuestos ADICIONAL
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice':
                                R312 += (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            if u.move_type == 'in_refund':
                                R312 -= (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R322 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            if u.move_type == 'in_refund':
                                R322 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_ga -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_ga += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido  -->
                                if u.move_type == 'in_refund':
                                    iva_percibido_ga -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_ga += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))

                        #Calculamos los impuestos GENERAL
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice':
                                R31 += (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            if u.move_type == 'in_refund':
                                R31 -= (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R32 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            if u.move_type == 'in_refund':
                                R32 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_g -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_g += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if u.move_type == 'in_refund':
                                    iva_percibido_g -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_g += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))

                        #Calculamos el TOTAL de impuestos EXENTOS
                        if u.move_type == 'in_invoice':
                            untaxed += exento
                        if u.move_type == 'in_refund':
                            untaxed -= exento
                        if u.move_type == 'in_invoice':
                            R30 += exento
                        if u.move_type == 'in_refund':
                            R30 -= exento
                        #Retenciones
                        if u.move_type == 'in_invoice':
                            retencion += u.wh_id.total_tax_ret
                        if u.move_type == 'in_refund':
                            retencion -= u.wh_id.total_tax_ret
                        #TOTAL de IMPUESTOS (Reducido + General + Adicional)
                        if u.move_type == 'in_invoice':
                            tax += u.amount_tax
                        if u.move_type == 'in_refund':
                            tax -= u.amount_tax
                        #IVA PERCIBIDO
                        if u.move_type == 'in_invoice': 
                            iva_percibido += ((u.amount_tax)-(u.wh_id.total_tax_ret))
                        if u.move_type == 'in_refund':
                            iva_percibido -= ((u.amount_tax)-(u.wh_id.total_tax_ret))
                        #TERMINAN LOS CALCULOS
                    
                else:
                    if u.state !='annulled':
                        #EMPIEZAN LOS CALCULOS
                        if u.move_type == 'in_invoice':
                            total += (sum(u.mapped('amount_total')) *u.manual_currency_exchange_rate)
                        if u.move_type == 'in_refund':
                            total -= (sum(u.mapped('amount_total')) *u.manual_currency_exchange_rate)
            
                        #Calculamos el Exento
                        exento = (sum(u.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))  *u.manual_currency_exchange_rate)
                        #Calculamos los impuestos REDUCIDOS
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice': 
                                R333 += (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            if u.move_type == 'in_refund':
                                R333 -= (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R343 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            if u.move_type == 'in_refund':
                                R343 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate

                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_r -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_r += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if u.move_type == 'in_refund':
                                    iva_percibido_r -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_r += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')))*retention))

                        #Calculamos los impuestos ADICIONAL
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice':
                                R332 += (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            if u.move_type == 'in_refund':
                                R332 -= (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R342 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            if u.move_type == 'in_refund':
                                R342 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            #Iva Percibido
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_ga -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_ga += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido  -->
                                if u.move_type == 'in_refund':
                                    iva_percibido_ga -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_ga += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')))*retention))

                        #Calculamos los impuestos GENERAL
                        if len(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general')))):
                            #Base imponible del Impuesto
                            if u.move_type == 'in_invoice':
                                R33 += (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            if u.move_type == 'in_refund':
                                R33 -= (sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                            #Monto del Impuesto
                            if u.move_type == 'in_invoice':
                                R34 += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            if u.move_type == 'in_refund':
                                R34 -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))) *u.manual_currency_exchange_rate
                            #Iva Percibido - IVA RETENIDO POR EL COMPRADOR
                            if u.wh_id:
                                #IVA RETENIDO POR EL COMPRADOR
                                if u.move_type == 'in_refund':
                                    retencion_g -= ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                if u.move_type == 'in_invoice':
                                    retencion_g += ((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention)
                                #Iva Percibido
                                if u.move_type == 'in_refund':
                                    iva_percibido_g -= (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))
                                if u.move_type == 'in_invoice':
                                    iva_percibido_g += (sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))-((sum(u.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')))*retention))

                        #Calculamos el TOTAL de impuestos EXENTOS
                        if u.move_type == 'in_invoice':
                            untaxed += exento
                        if u.move_type == 'in_refund':
                            untaxed -= exento
                        if u.move_type == 'in_invoice':
                            R30 += exento
                        if u.move_type == 'in_refund':
                            R30 -= exento
                        #Retenciones
                        if u.move_type == 'in_invoice':
                            retencion += u.wh_id.total_tax_ret
                        if u.move_type == 'in_refund':
                            retencion -= u.wh_id.total_tax_ret
                        #TOTAL de IMPUESTOS (Reducido + General + Adicional)
                        if u.move_type == 'in_invoice':
                            tax += u.amount_tax
                        if u.move_type == 'in_refund':
                            tax -= u.amount_tax
                        #IVA PERCIBIDO
                        if u.move_type == 'in_invoice': 
                            iva_percibido += ((u.amount_tax)-(u.wh_id.total_tax_ret))
                        if u.move_type == 'in_refund':
                            iva_percibido -= ((u.amount_tax)-(u.wh_id.total_tax_ret))
                    #TERMINAN LOS CALCULOS
        
           
                worksheet.write(rows, 0, cont, header_data_format)
                worksheet.write_datetime(rows,1, u.invoice_date, fecha)
                worksheet.write(rows,2, u.partner_id.rif, header_data_format)
                worksheet.write(rows,3, u.partner_id.name, header_data_format)
                worksheet.write(rows,4, '-', header_data_format) #serie
                worksheet.write(rows,5, u.partner_id.residence_type, header_data_format) #tipo de proveedor
                worksheet.write(rows,6, u.vendor_invoice_number, header_data_format)
                worksheet.write(rows,7, u.nro_control, header_data_format)#Número de Control de Factura
                worksheet.write(rows,8, u.num_import, header_data_format)#Número de Planilla de Importación
                worksheet.write(rows,9, u.num_export, header_data_format)#Número de Expediente Importación
                worksheet.write(rows,10, '-', header_data_format)#Número Nota de Débito
                worksheet.write(rows,11, u.vendor_invoice_number if u.move_type == 'in_refund' else '-', header_data_format)#Número Nota de Crédito
                worksheet.write(rows,12, u.mapped('reversed_entry_id').ref if u.move_type == 'in_refund' else '-', header_data_format)
                worksheet.write(rows,13, (sum(u.mapped('amount_total')) *u.manual_currency_exchange_rate) if u.move_type == 'in_refund' else (sum(u.mapped('amount_total')) *u.manual_currency_exchange_rate), currency_format)
                #Total Compras Incluyendo el IVA                
                monto_impuesto = (sum(u.invoice_line_ids.mapped('tax_ids.amount')) *u.manual_currency_exchange_rate)
                monto_impuesto_untaxed = (sum(u.invoice_line_ids.filtered(lambda whl: not whl.tax_ids).mapped('price_subtotal')) + sum(u.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                monto_impuesto_untaxed_exento = (sum(u.invoice_line_ids.filtered(lambda whl: len(whl.tax_ids) == 0).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                
                if monto_impuesto == 0 or monto_impuesto_untaxed > 0 or monto_impuesto_untaxed_exento:
                    worksheet.write(rows,14, exento*-1 if u.move_type == 'in_refund' else exento, currency_format)
                    acum_exento += (exento)
                else:
                    worksheet.write(rows,14, 0.0, currency_format)
                
                worksheet.write(rows,15, '-', header_data_format)#exoneradas
                worksheet.write(rows,16, '-', header_data_format)#no sujetas
                
                
                #IVA NO DEDUCIBLE
                if not u.deductible:
                    if u.move_type == 'in_invoice':
                        tax_deductible += u.amount_tax
                    if u.move_type == 'in_refund':
                        tax_deductible -= u.amount_tax
                    if u.move_type == 'in_invoice':
                        untaxed_deductible += (sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                    if u.move_type == 'in_refund':
                        untaxed_deductible -= (sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                    if sum(u.invoice_line_ids.mapped('tax_ids.amount')) > 0:
                        worksheet.write(rows,17, (sum(u.mapped('amount_total')) - (exento + u.amount_tax))*-1 if u.move_type == 'in_refund' else (sum(u.mapped('amount_untaxed'))*u.manual_currency_exchange_rate) - exento, currency_format)
                    else:
                        worksheet.write(rows,17, 0.0, currency_format)
                    iva_dedu=(sum(u.mapped('amount_untaxed'))*u.manual_currency_exchange_rate) - exento
                    worksheet.write(rows,18, sum(u.invoice_line_ids.mapped('tax_ids.amount')), currency_format)#Porcentaje Alicuota
                    worksheet.write(rows,19, (iva_dedu/100)*sum(u.invoice_line_ids.mapped('tax_ids.amount')) if u.move_type == 'in_refund' else (iva_dedu/100)*sum(u.invoice_line_ids.mapped('tax_ids.amount')), currency_format)
                    worksheet.write(rows,20, '-', header_data_format)
                    worksheet.write(rows,21, '-', header_data_format)
                    worksheet.write(rows,22, '-', header_data_format)

                    total_dedu += (iva_dedu/100)*sum(u.invoice_line_ids.mapped('tax_ids.amount'))
                #Compras Exentas
                if u.deductible:
                    if u.move_type == 'in_invoice':
                        tax_not_deductible += u.amount_tax
                    if u.move_type == 'in_refund':
                        tax_not_deductible -= u.amount_tax
                    if u.move_type == 'in_invoice':
                        untaxed_not_deductible += (sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                    if u.move_type == 'in_refund':
                        untaxed_not_deductible -= (sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal')) *u.manual_currency_exchange_rate)
                    
                    worksheet.write(rows,17, '-', header_data_format)
                    worksheet.write(rows,18, '-', header_data_format)
                    worksheet.write(rows,19, '-', header_data_format)
                    
                    worksheet.write(rows,20, sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal'))*-1 if u.move_type == 'in_refund' else sum(u.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped('price_subtotal')), currency_format)
                    worksheet.write(rows,21, sum(u.invoice_line_ids.mapped('tax_ids.amount')), currency_format)
                    worksheet.write(rows,22, u.amount_tax*-1 if u.move_type == 'in_refund' else u.amount_tax, currency_format)

                #Monto Impuesto
                worksheet.write(rows,23, '', currency_format)
                
                #IVA  Retenido al VENDEDOR -->
                worksheet.write(rows,24, '', currency_format)#porcentaje ret
                
                #IVA RETENIDO a Terceros
                worksheet.write(rows,25, '', currency_format)#Prorrata
                    
                #linea de las retenciones
            for ret in dict_fact['rete'].sorted(lambda r: (r.retention_id.date, r.retention_id.id)):
                rows += 1
                cont += 1
                worksheet.write(rows, 0, cont, header_data_format)
                worksheet.write_datetime(rows,1, ret.retention_id.date, fecha)#Fecha de la retención
                worksheet.write(rows,2, ret.retention_id.partner_id.rif, header_data_format)#RIF
                worksheet.write(rows,3, ret.retention_id.partner_id.name, header_data_format)#Nombre o Razón social
                worksheet.write(rows,4, '-',header_data_format)
                worksheet.write(rows,5, ret.retention_id.partner_id.residence_type, header_data_format)#Tipo de Proveedor
                worksheet.write(rows,6, '-', header_data_format)#nmero de factura
                worksheet.write(rows,7, ret.invoice_id.nro_control, header_data_format)#Número de Control de Factura
                worksheet.write(rows,8, '-', header_data_format)#Número de Planilla de Importación
                worksheet.write(rows,9, '-', header_data_format)#Número de Expediente Importación
                worksheet.write(rows,10, '-', header_data_format)#Número Nota de Débito
                worksheet.write(rows,11, '-', header_data_format)#Número Nota de Crédito
                worksheet.write(rows,12, ret.invoice_id.vendor_invoice_number, header_data_format)#numero de factura afectada
                worksheet.write(rows,13, '-', header_data_format)#t compras inclydo iva
                worksheet.write(rows,14, '-', header_data_format)#exento
                worksheet.write(rows,15, '-', header_data_format)#exoneradas
                worksheet.write(rows,16, '-', header_data_format)#no sujetas
                worksheet.write(rows,17, '-', header_data_format)#base imponible
                worksheet.write(rows,18, '-', header_data_format)#aliq
                worksheet.write(rows,19, '-', header_data_format)#imp. iva
                worksheet.write(rows,20, '-', header_data_format)#base imp
                worksheet.write(rows,21, '-', header_data_format)#aliq
                worksheet.write(rows,22, '-', header_data_format)#imp iva
                worksheet.write(rows,23, ret.ret_amount*-1 if ret.retention_id.move_type == 'in_refund' else ret.ret_amount, currency_format)#iva retenido al vendedor
                acumret += ret.ret_amount
                worksheet.write(rows,24, ret.rate_amount*-1 if ret.retention_id.move_type == 'in_refund' else ret.rate_amount, currency_format)#porcentaje ret
                worksheet.write(rows,25, ret.retention_id.number if ret.retention_id.move_type == 'in_refund' else ret.retention_id.number, currency_format)#comprobante de retencion

            worksheet.write(rows+1,13, total, currency_format)
            worksheet.write(rows+1,14, acum_exento, currency_format)
            worksheet.write(rows+1,15, 0.0, currency_format)
            worksheet.write(rows+1,16, 0.0, currency_format)                         
            #DEDUCIBLE INICIO
            worksheet.write(rows+1,17, R33 + R31 + R312 + R313 + R332 + R333, currency_format)
            worksheet.write(rows+1,18, 0.0, currency_format)
            worksheet.write(rows+1,19, total_dedu , currency_format)
            #DEDUCIBLE FIN
            R30 = acum_exento
            #NO DEDUCIBLE INICIO
            worksheet.write(rows+1,20, untaxed_not_deductible, currency_format)
            worksheet.write(rows+1,21, 0.0, currency_format)
            worksheet.write(rows+1,22, tax_not_deductible, currency_format)
            #MO DEDUCIBLE FIN
            # R34 = tax
            worksheet.write(rows+1,23, retencion, currency_format)
            worksheet.write(rows+1,24, '-', currency_format)

            #Se definen las variables dependientes de otras
            # R34 =R34-R342-R343
            # R342 =R342-R322
            # R343 =R343-R323
            R35 =R30+R332+R333+R33+R312+R313+R31
            R36 =R34+R342+R343+R32+R322+R323

            #TABLA ADICIONAL
            #ESTRUCTURA DE LA TABLA
            #COLUMNAS
            worksheet.write(rows+3, 18,'', header_data_format)#1
            worksheet.merge_range(rows+3, 19, rows+3, 20,  'Base imponible', header_data_format) #2
            worksheet.write(rows+3, 21,'', header_data_format) #3
            worksheet.merge_range(rows+3, 22, rows+3, 23,  'Crédito Fiscal', header_data_format)  #4
            worksheet.merge_range(rows+3, 24, rows+3, 25,  'IVA Retenido (al Vendedor)', header_data_format)#5

            #FILAS
            worksheet.merge_range(rows+4, 12, rows+4, 17,  'Total : Compras Excentas y/o sin derecho a crédito fiscal', header_data_format)
            worksheet.merge_range(rows+5, 12, rows+5, 17,  'Compras Importación afectadas solo Alicuota General', header_data_format)
            worksheet.merge_range(rows+6, 12, rows+6, 17,  'Compras Importación Afectas en Alicuota General + Adicional', header_data_format)
            worksheet.merge_range(rows+7, 12, rows+7, 17,  'Compras Importación Afectas en Alicuota Reducida', header_data_format)
            worksheet.merge_range(rows+8, 12, rows+8, 17,  'Compras Internas Afectas en Alicuota General + Adicional', header_data_format)
            worksheet.merge_range(rows+9, 12, rows+9, 17,  'Compras Internas Afectas en Alicuota Reducida', header_data_format)
            worksheet.merge_range(rows+10, 12, rows+10, 17,'Compras Internas Afectas solo Alicuota General', header_data_format)
            worksheet.merge_range(rows+11, 12, rows+11, 17,'TOTAL', header_data_format)

            worksheet.write(rows+4, 18,'30', header_data_format)                        #1
            worksheet.write(rows+5, 18,'31', header_data_format)                        #1
            worksheet.write(rows+6, 18,'312', header_data_format)                       #1
            worksheet.write(rows+7, 18,'313', header_data_format)                       #1
            worksheet.write(rows+8, 18,'332', header_data_format)                       #1
            worksheet.write(rows+9, 18,'333', header_data_format)                       #1
            worksheet.write(rows+10, 18,'33', header_data_format)                       #1
            worksheet.write(rows+11, 18,'35', header_data_format)                       #1

            worksheet.write(rows+4,  21,'', header_data_format)                         #3
            worksheet.write(rows+5,  21,'32', header_data_format)                       #3
            worksheet.write(rows+6,  21,'322', header_data_format)                      #3
            worksheet.write(rows+7,  21,'323', header_data_format)                      #3
            worksheet.write(rows+8,  21,'342', header_data_format)                      #3
            worksheet.write(rows+9,  21,'343', header_data_format)                      #3
            worksheet.write(rows+10, 21,'34', header_data_format)                       #3
            worksheet.write(rows+11, 21,'36', header_data_format)                       #3

            worksheet.merge_range(rows+4, 19, rows+4, 20,  R30, currency_format)        #2
            worksheet.merge_range(rows+5, 19, rows+5, 20,  R31, currency_format)        #2
            worksheet.merge_range(rows+6, 19, rows+6, 20,  R312, currency_format)       #2
            worksheet.merge_range(rows+7, 19, rows+7, 20,  R313, currency_format)       #2
            worksheet.merge_range(rows+8, 19, rows+8, 20,  R332, currency_format)       #2
            worksheet.merge_range(rows+9, 19, rows+9, 20,  R333, currency_format)       #2
            worksheet.merge_range(rows+10, 19, rows+10, 20,  R33, currency_format)      #2
            worksheet.merge_range(rows+11, 19, rows+11, 20,  R35, currency_format)      #2

            worksheet.merge_range(rows+4, 22, rows+4, 23,  0.0, currency_format)        #4
            worksheet.merge_range(rows+5, 22, rows+5, 23,  R32, currency_format)        #4
            worksheet.merge_range(rows+6, 22, rows+6, 23,  R322, currency_format)       #4
            worksheet.merge_range(rows+7, 22, rows+7, 23,  R323, currency_format)       #4
            worksheet.merge_range(rows+8, 22, rows+8, 23,  R342, currency_format)       #4
            worksheet.merge_range(rows+9, 22, rows+9, 23,  R343, currency_format)       #4
            worksheet.merge_range(rows+10, 22, rows+10, 23, R34, currency_format)      #4
            worksheet.merge_range(rows+11, 22, rows+11, 23, R36, currency_format)      #4

            worksheet.merge_range(rows+4, 24, rows+4, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+5, 24, rows+5, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+6, 24, rows+6, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+7, 24, rows+7, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+8, 24, rows+8, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+9, 24, rows+9, 25,  0.0, currency_format)        #5
            worksheet.merge_range(rows+10, 24, rows+10, 25,  acumret, currency_format)  #5
            worksheet.merge_range(rows+11, 24, rows+11, 25,  acumret, currency_format)  #5

            #ULTIMA TABLA
            #COLUMNAS

            worksheet.merge_range(rows+13, 21, rows+13, 25, 'Resumen Tasa General', header_data_format)
            worksheet.write(rows+14,  21,'Tasa', header_data_format)
            worksheet.merge_range(rows+14, 22, rows+14, 23, 'Base Imponible', header_data_format)
            worksheet.merge_range(rows+14, 24, rows+14, 25, 'Debito Fiscal', header_data_format)

            worksheet.write(rows+15,  21,'16%', header_data_format)
            worksheet.merge_range(rows+15, 22, rows+15, 23, R33 if R33 else 0.0, currency_format)
            worksheet.merge_range(rows+15, 24, rows+15, 25, R34 if R34 else 0.0, currency_format)
            
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