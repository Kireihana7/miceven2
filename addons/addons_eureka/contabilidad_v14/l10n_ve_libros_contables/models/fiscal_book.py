import time
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from datetime import timedelta, datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlsxwriter
import base64
from io import BytesIO

class FiscalBook(models.Model):
    _description = "Libro de Ventas y Compras"
    _name = 'fiscal.book'
    _inherit = ['mail.thread']
    _rec_rame = 'fiscal_book_rec'

    STATES = [('draft', 'Preparándose'),
    ('confirmed', 'Aprobado por el Responsable'),
    ('done', 'Enviado al Seniat'),
    ('cancel', 'Cancelar')]

    TYPES = [('sale', 'Libro de Venta'),
    ('purchase', 'Libro de Compra')]

    @api.model
    def _get_type(self):
        context = self._context or {}
        return context.get('type', 'purchase')

    name = fields.Char('Descripción', size=256, required=True)
    data = fields.Binary(string='Archivo', readonly=True)    
    company_id = fields.Many2one(
    'res.company', string='Compañia',
        default=lambda self: self.env.company.id,
        help="Compañia", required=True)
    currency_id = fields.Many2one('res.currency', string='Moneda')
    period_start = fields.Date('Periodo de Inicio',required=True)
    period_end = fields.Date('Periodo Fin',required=True)
    
    def _get_journal_ids(self):
        tipo = self._context.get('type', 'purchase')
        domain =[('type','=',tipo)]
        # journal_list=[]
        # some_model = self.env['account.journal'].search([('type','=',tipo),('is_fiscal','=',True)])
        # for each in some_model:
        #     journal_list.append(each.id)
        # if journal_list:
        #     domain = [('id', 'in', journal_list),('is_fiscal','=',True)]
        #     return domain
        return domain
    journal_ids = fields.Many2many('account.journal', string='Diarios',
        required=True,
        default=lambda self: self.env['account.journal'].search([('type', '=',self._context.get('type', 'purchase')),('is_fiscal','=',True)]),
        domain=_get_journal_ids)
    state = fields.Selection(STATES, string='Status', required=True, readonly=True, default='draft')
    type = fields.Selection(TYPES, help="Select Sale for Customers and Purchase for Suppliers",
     string='Tipo de libro', required=True, default=lambda s: s._get_type())

    base_amount = fields.Float('Base imponible', help='Cantidad utilizada como base imponible')
    tax_amount = fields.Float('Cantidad gravada', help='Cantidad gravada sobre la base imponible')

    # Tabla de Líneas para Facturas
    fbl_ids = fields.One2many('fiscal.book.line', 'fiscal_id', 'Lineas de libros',
    help='Lines being recorded in the book')
      
    # Facturas Relacionadas
    invoice_ids = fields.One2many('account.move', 'fiscal_id', 'Facturas', help="Facturas vinculadas al libro ")

    #Retenciones asociadas
    retention_ids = fields.One2many('fiscal.book.retention', 'fiscal_id', 'Retenciones', help="Las retenciones asociadas al libro")

    # Facturas Relacionadas en Borrador
    issue_invoice_ids = fields.One2many('fiscal.book.issues', 'fiscal_id', 'Facturas con Incidencias',
     help="Las facturas que están en estado pendiente cancelan o se borran")
    issues_count = fields.Boolean(string="Tiene Incidencias",compute="_compute_issues_count")

    # Retenciones relacionadas
    iwdl_ids = fields.One2many('account.wh.iva.line', 'fiscal_id', 'Retenciones de IVA',
     help="Retenciones de IVA registradas en un libro fiscal")

    note = fields.Text('Note')

    # Monto de Las retenciones
    get_wh_sum = fields.Float(compute='_compute_amounts',
    method=True, store=True,
    string="Retención del período actual",
    help="Usado en"
    " 1. Fila de totalización en el bloque de la línea del libro fiscal en la retención"
    " Columna de -iva"
    " 2. Second row at the Withholding Summary block ")

    # Monto de las retenciones mes pasado
    whi_previous_amount = fields.Float( compute='_compute_amounts',
    method=True, store=True,
    string="Retención del período anterior",
    help="Primera fila en el bloque Resumen de retención")
   
    #Monto de Todas las retenciones (Anterior y actuales)
    whi_actual_amount = fields.Float(compute='_compute_amounts',
    method=True, store=True,
    string="Suma de retención de IVA",
    help="Fila de totalización en el bloque Resumen de retención")

    # Monto Imponible con IVA
    base_imponible_impuesto = fields.Float(compute='_compute_amounts',
    method=True, store=True,
    string='Importe total con IVA',
    help="Total con suma de IVA (importación / exportación, nacional, contribuyente y "
    "Pagador no tributario")

    # Monto Imponible EXENTO
    base_imponible_exento = fields.Float(compute='_compute_amounts',
    method=True, store=True,
    string="Base Imponible Exento",)


    total_with_iva = fields.Float('Total Facturas',compute="_compute_amounts")
    total_vat_exempt = fields.Float("Total Exento",compute="_compute_amounts")
    total_vat_reduced_base = fields.Float("Total Base Reducida",compute="_compute_amounts")
    total_vat_reduced_tax = fields.Float("IVA Reducida",compute="_compute_amounts")
    total_vat_general_base = fields.Float("Base Imponible",compute="_compute_amounts")
    total_vat_general_tax = fields.Float("IVA",compute="_compute_amounts")
    total_vat_additional_base = fields.Float("Base Adicional",compute="_compute_amounts")
    total_vat_additional_tax = fields.Float("IVA Adicional",compute="_compute_amounts")

    @api.depends('issue_invoice_ids')
    def _compute_issues_count(self):
        for rec in self:
            rec.issues_count = True if len(rec.issue_invoice_ids) > 0 else False

    @api.depends('company_id','currency_id','period_start','period_end','fbl_ids','retention_ids')
    def _compute_amounts(self):
        for rec in self:
            lines = rec.mapped('fbl_ids')
            rec.get_wh_sum = sum(rec.retention_ids.mapped('ret_amount'))
            rec.whi_previous_amount = 0
            rec.whi_actual_amount = 0
            rec.base_imponible_impuesto = 0
            rec.base_imponible_exento = 0
            rec.total_with_iva = sum(lines.mapped('total_with_iva'))
            rec.total_vat_exempt = sum(lines.mapped('vat_exempt'))
            rec.total_vat_reduced_base = sum(lines.mapped('vat_reduced_base'))
            rec.total_vat_reduced_tax = sum(lines.mapped('vat_reduced_tax'))
            rec.total_vat_general_base = sum(lines.mapped('vat_general_base'))
            rec.total_vat_general_tax = sum(lines.mapped('vat_general_tax'))
            rec.total_vat_additional_base = sum(lines.mapped('vat_additional_base'))
            rec.total_vat_additional_tax = sum(lines.mapped('vat_additional_tax'))

    def update_book(self):
        for rec in self:
            # Libros de Ventas
            if rec.type == 'sale':
                line_dict = {}
                if rec.fbl_ids:
                    # Si tiene líneas, se borran
                    for lines in rec.fbl_ids:
                        values = [(5, 0, 0)]
                        rec.update({'fbl_ids': values})
                if rec.issue_invoice_ids:
                    # Si tiene líneas, se borran
                    for lines in rec.issue_invoice_ids:
                        values = [(5, 0, 0)]
                        rec.update({'issue_invoice_ids': values})
                if rec.retention_ids:
                    # Si tiene líneas, se borran
                    for lines in rec.retention_ids:
                        values = [(5, 0, 0)]
                        rec.update({'retention_ids': values})
                #Busqueda de las facturas en el periodo, diario, tipo
                # retentions=self.env['account.wh.iva'].search([('date','>=',rec.period_start),('date','<=',rec.period_end),('company_id','=',rec.company_id.id)]).ids
                # domain=["&",('company_id','=',rec.company_id.id),"|","&","&",('date','>=',rec.period_start),('date','<=',rec.period_end),('journal_id','in',rec.journal_ids.ids),["wh_id","in",retentions]]
                
                orders = [line for line in sorted(self.env['account.move'].search([('date','>=',rec.period_start),('date','<=',rec.period_end),('journal_id','in',rec.journal_ids.ids),('company_id','=',rec.company_id.id)]),
                    key=lambda x: x.id)]
                for order in orders:
                    multiplicador = 1 if order.move_type in ('in_invoice','out_invoice') else -1
                    # Si la Factura está confirmada, se añaden bajo un criterio
                    if order.state == 'posted':
                        if order.currency_id == order.company_id.currency_id:
                            line_dict = {
                                'base':  abs(order.amount_untaxed * order.manual_currency_exchange_rate) * multiplicador,
                                'amount':  abs(order.amount_total * order.manual_currency_exchange_rate) * multiplicador,
                                'name': order.name,
                                'invoice_id':order.id,
                                'iwdl_id':order.wh_id.wh_lines[0].id if order.wh_id and order.wh_id.wh_lines else False,
                                'emission_date':order.invoice_date,
                                'accounting_date':order.date,
                                'doc_type':order.move_type,
                                'partner_name':order.partner_id.name,
                                'people_type':order.partner_id.residence_type,
                                'partner_vat':order.partner_id.vat,
                                'affected_invoice':order.debit_origin_id.name if order.debit_origin_id else order.parent_id.name if order.parent_id else '-',
                                'get_wh_vat':order.wh_id.id if order.wh_id else False,
                                'wh_number':order.wh_id.customer_doc_number if rec.type == 'sale' else order.wh_id.number,
                                'affected_invoice_date':order.wh_id.date if order.wh_id else False,
                                'wh_rate': 100.00 if order.retention=='03-ordinary' else 75.0 if order.retention=='02-special' else 0 ,
                                'wh_amount': abs((order.wh_id.total_tax_ret * order.wh_id.manual_currency_exchange_rate) if order.wh_id else 0) * multiplicador,
                                'get_wh_debit_credit':(abs(order.amount_tax * order.manual_currency_exchange_rate)) * multiplicador,
                                'ctrl_number':order.nro_control,
                                'invoice_number':order.name,
                                'debit_affected':order.debit_origin_id.name if order.debit_origin_id else '-',
                                'credit_affected':order.parent_id.name if order.parent_id else '-',
                                'type':order.transaction_type,
                                'total_with_iva':abs(order.amount_total * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_exempt':abs((sum(order.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_reduced_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_reduced_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_general_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_general_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_additional_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_additional_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                            }
                        else:
                            line_dict = {
                                'base':  abs(order.amount_untaxed) * multiplicador,
                                'amount':  abs(order.amount_total) * multiplicador,
                                'name': order.name,
                                'invoice_id':order.id,
                                'iwdl_id':order.wh_id.wh_lines[0].id if order.wh_id and order.wh_id.wh_lines else False,
                                'emission_date':order.invoice_date,
                                'accounting_date':order.date,
                                'doc_type':order.move_type,
                                'partner_name':order.partner_id.name,
                                'people_type':order.partner_id.residence_type,
                                'partner_vat':order.partner_id.vat,
                                'affected_invoice':order.debit_origin_id.name if order.debit_origin_id else order.parent_id.name if order.parent_id else '-',
                                'get_wh_vat':order.wh_id.id if order.wh_id else False,
                                'wh_number':order.wh_id.customer_doc_number if rec.type == 'sale' else order.wh_id.number,
                                'affected_invoice_date':order.wh_id.date if order.wh_id else False,
                                'wh_rate': 100.00 if order.retention=='03-ordinary' else 75.0 if order.retention=='02-special' else 0 ,
                                'wh_amount': abs((order.wh_id.total_tax_ret * order.wh_id.manual_currency_exchange_rate) if order.wh_id else 0) * multiplicador,
                                'get_wh_debit_credit':abs(order.amount_tax) * multiplicador,
                                'ctrl_number':order.nro_control,
                                'invoice_number':order.name,
                                'debit_affected':order.debit_origin_id.name if order.debit_origin_id else '-',
                                'credit_affected':order.parent_id.name if order.parent_id else '-',
                                'type':order.transaction_type,
                                'total_with_iva':abs(order.amount_total) * multiplicador,
                                'vat_exempt':abs(sum(order.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))) * multiplicador,
                                'vat_reduced_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_reduced_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_general_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_general_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_additional_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_additional_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))) * multiplicador,
                            }
                        lines = [(0,0,line_dict)]
                        rec.write({'fbl_ids':lines})
                    # Si la factura está cancelada y su nombre es diferente a / 
                    # además de que tenga fecha, se añade.se
                    # Con esto se evita facturas que fueron creadas de manera erronea
                    if order.state == 'cancel' and order.name !='/' and order.invoice_date != False:
                        line_dict = {
                                'base':  0,
                                'amount':  0,
                                'name': order.name,
                                'invoice_id':order.id,
                                'iwdl_id':order.wh_id.wh_lines[0].id if order.wh_id and order.wh_id.wh_lines else False,
                                'emission_date':order.invoice_date,
                                'accounting_date':order.date,
                                'doc_type':order.move_type,
                                'partner_name':order.partner_id.name,
                                'people_type':order.partner_id.residence_type,
                                'partner_vat':order.partner_id.vat,
                                'affected_invoice':order.debit_origin_id.name if order.debit_origin_id else order.parent_id.name if order.parent_id else '-',
                                'get_wh_vat':order.wh_id.id if order.wh_id else False,
                                'wh_number':order.wh_id.customer_doc_number if rec.type == 'sale' else order.wh_id.number,
                                'affected_invoice_date':order.wh_id.date if order.wh_id else False,
                                'wh_rate': 100.00 if order.retention=='03-ordinary' else 75.0 if order.retention=='02-special' else 0 ,
                                'wh_amount': 0,
                                'get_wh_debit_credit':0,
                                'ctrl_number':order.nro_control,
                                'invoice_number':order.name,
                                'debit_affected':order.debit_origin_id.name if order.debit_origin_id else '-',
                                'credit_affected':order.parent_id.name if order.parent_id else '-',
                                'type':order.transaction_type,
                                'total_with_iva':0,
                                'vat_exempt':0,
                                'vat_reduced_base':0,
                                'vat_reduced_tax':0,
                                'vat_general_base':0,
                                'vat_general_tax':0,
                                'vat_additional_base':0,
                                'vat_additional_tax':0,
                            }
                        lines = [(0,0,line_dict)]
                        rec.write({'fbl_ids':lines})
                    # Si están en borrador, se añade como facturas con problemas
                    if order.state == 'draft':
                        line_dict = {
                                'name': order.name,
                                'invoice_id':order.id,
                                'partner_name':order.partner_id.name,
                            }
                        lines = [(0,0,line_dict)]
                        rec.write({'issue_invoice_ids':lines})
                retentions=self.env['account.wh.iva'].search([('state','not in',('cancel','draft')),('move_type','in',('out_invoice','out_refund')),('date','>=',self.period_start),('date','<=',self.period_end),('company_id','=',self.company_id.id)]).mapped('wh_lines')
                for rete in retentions:
                    multiplicador = 1 if rete.retention_id.move_type in ('in_invoice','out_invoice') else -1
                    line_dict = {           
                            'ret_amount':  abs(rete.ret_amount) * rete.retention_id.manual_currency_exchange_rate * multiplicador,
                            'rate_amount':  rete.rate_amount,
                            'name': rete.retention_id.number,
                            'retention_id':rete.retention_id.id,
                            'invoice_id':rete.invoice_id.id,
                            'retention_line_id':rete.id,
                            'date':rete.retention_id.date,
                        }
                    lines = [(0,0,line_dict)]
                    rec.write({'retention_ids':lines})
                if not line_dict:
                    raise UserError(_("Nada para declarar."))
            # Libros de Compras
            if rec.type == 'purchase':
                line_dict = {}
                if rec.fbl_ids:
                    # Si tiene líneas, se borran
                    for lines in rec.fbl_ids:
                        values = [(5, 0, 0)]
                        rec.update({'fbl_ids': values})
                if rec.issue_invoice_ids:
                    # Si tiene líneas, se borran
                    for lines in rec.issue_invoice_ids:
                        values = [(5, 0, 0)]
                        rec.update({'issue_invoice_ids': values})
                if rec.retention_ids:
                    # Si tiene líneas, se borran
                    for lines in rec.retention_ids:
                        values = [(5, 0, 0)]
                        rec.update({'retention_ids': values})
                #Busqueda de las facturas en el periodo, diario, tipo
                # domain=["&",('company_id','=',rec.company_id.id),"|","&","&",('date','>=',rec.period_start),('date','<=',rec.period_end),('journal_id','in',rec.journal_ids.ids),["wh_id","in",retentions]]
                
                orders = [line for line in sorted(self.env['account.move'].search([('date','>=',rec.period_start),('date','<=',rec.period_end),('journal_id','in',rec.journal_ids.ids),('company_id','=',rec.company_id.id)]),
                    key=lambda x: x.id)]
                for order in orders:
                    multiplicador = 1 if order.move_type in ('in_invoice','out_invoice') else -1
                    # Si la Factura está confirmada, se añaden bajo un criterio
                    if order.state == 'posted':
                        if order.currency_id == order.company_id.currency_id:
                            line_dict = {
                                'base':  abs(order.amount_untaxed * order.manual_currency_exchange_rate) * multiplicador,
                                'amount':  abs(order.amount_total * order.manual_currency_exchange_rate) * multiplicador,
                                'name': order.name,
                                'invoice_id':order.id,
                                'iwdl_id':order.wh_id.wh_lines[0].id if order.wh_id and order.wh_id.wh_lines else False,
                                'emission_date':order.invoice_date,
                                'accounting_date':order.date,
                                'doc_type':order.move_type,
                                'partner_name':order.partner_id.name,
                                'people_type':order.partner_id.residence_type,
                                'partner_vat':order.partner_id.vat,
                                'affected_invoice':order.debit_origin_id.name if order.debit_origin_id else order.parent_id.name if order.parent_id else '-',
                                'get_wh_vat':order.wh_id.id if order.wh_id else False,
                                'wh_number':order.wh_id.customer_doc_number if rec.type == 'sale' else order.wh_id.number,
                                'affected_invoice_date':order.wh_id.date if order.wh_id else False,
                                'wh_rate': 100.00 if order.retention=='03-ordinary' else 75.0 if order.retention=='02-special' else 0 ,
                                'wh_amount': abs((order.wh_id.total_tax_ret * order.wh_id.manual_currency_exchange_rate) if order.wh_id else 0) * multiplicador,
                                'get_wh_debit_credit':(abs(order.amount_tax * order.manual_currency_exchange_rate)) * multiplicador,
                                'ctrl_number':order.nro_control,
                                'invoice_number':order.name,
                                'debit_affected':order.debit_origin_id.name if order.debit_origin_id else '-',
                                'credit_affected':order.parent_id.name if order.parent_id else '-',
                                'type':order.transaction_type,
                                'total_with_iva':abs(order.amount_total * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_exempt':abs((sum(order.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_reduced_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_reduced_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_general_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_general_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_additional_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                                'vat_additional_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal')) * order.manual_currency_exchange_rate) * multiplicador,
                            }
                        else:
                            line_dict = {
                                'base':  abs(order.amount_untaxed) * multiplicador,
                                'amount':  abs(order.amount_total) * multiplicador,
                                'name': order.name,
                                'invoice_id':order.id,
                                'iwdl_id':order.wh_id.wh_lines[0].id if order.wh_id and order.wh_id.wh_lines else False,
                                'emission_date':order.invoice_date,
                                'accounting_date':order.date,
                                'doc_type':order.move_type,
                                'partner_name':order.partner_id.name,
                                'people_type':order.partner_id.residence_type,
                                'partner_vat':order.partner_id.vat,
                                'affected_invoice':order.debit_origin_id.name if order.debit_origin_id else order.parent_id.name if order.parent_id else '-',
                                'get_wh_vat':order.wh_id.id if order.wh_id else False,
                                'wh_number':order.wh_id.customer_doc_number if rec.type == 'sale' else order.wh_id.number,
                                'affected_invoice_date':order.wh_id.date if order.wh_id else False,
                                'wh_rate': 100.00 if order.retention=='03-ordinary' else 75.0 if order.retention=='02-special' else 0 ,
                                'wh_amount': abs((order.wh_id.total_tax_ret * order.wh_id.manual_currency_exchange_rate) if order.wh_id else 0) * multiplicador,
                                'get_wh_debit_credit':abs(order.amount_tax) * multiplicador,
                                'ctrl_number':order.nro_control,
                                'invoice_number':order.name,
                                'debit_affected':order.debit_origin_id.name if order.debit_origin_id else '-',
                                'credit_affected':order.parent_id.name if order.parent_id else '-',
                                'type':order.transaction_type,
                                'total_with_iva':abs(order.amount_total) * multiplicador,
                                'vat_exempt':abs(sum(order.invoice_line_ids.filtered(lambda line: not len(line.tax_ids)).mapped('price_subtotal')) + sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.amount == 0))).mapped('price_subtotal'))) * multiplicador,
                                'vat_reduced_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_reduced_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_general_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_general_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_additional_base':abs(sum(order.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))) * multiplicador,
                                'vat_additional_tax':abs(sum(order.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped('price_subtotal'))) * multiplicador,
                            }
                        lines = [(0,0,line_dict)]
                        rec.write({'fbl_ids':lines})
                    # Si la factura está cancelada y su nombre es diferente a / 
                    # además de que tenga fecha, se añade.se
                    # Con esto se evita facturas que fueron creadas de manera erronea
                    # if order.state == 'cancel' and order.name !='/' and order.invoice_date != False:
                    #     line_dict = {
                    #             'base':  0,
                    #             'amount':  0,
                    #             'name': order.name,
                    #             'invoice_id':order.id,
                    #             'iwdl_id':order.wh_id.wh_lines[0].id if order.wh_id and order.wh_id.wh_lines else False,
                    #             'emission_date':order.invoice_date,
                    #             'accounting_date':order.date,
                    #             'doc_type':order.move_type,
                    #             'partner_name':order.partner_id.name,
                    #             'people_type':order.partner_id.residence_type,
                    #             'partner_vat':order.partner_id.vat,
                    #             'affected_invoice':order.debit_origin_id.name if order.debit_origin_id else order.parent_id.name if order.parent_id else '-',
                    #             'get_wh_vat':order.wh_id.id if order.wh_id else False,
                    #             'wh_number':order.wh_id.customer_doc_number if rec.type == 'sale' else order.wh_id.number,
                    #             'affected_invoice_date':order.wh_id.date if order.wh_id else False,
                    #             'wh_rate': 100.00 if order.retention=='03-ordinary' else 75.0 if order.retention=='02-special' else 0 ,
                    #             'wh_amount': 0,
                    #             'get_wh_debit_credit':0,
                    #             'ctrl_number':order.nro_control,
                    #             'invoice_number':order.name,
                    #             'debit_affected':order.debit_origin_id.name if order.debit_origin_id else '-',
                    #             'credit_affected':order.parent_id.name if order.parent_id else '-',
                    #             'type':order.transaction_type,
                    #             'total_with_iva':0,
                    #             'vat_exempt':0,
                    #             'vat_reduced_base':0,
                    #             'vat_reduced_tax':0,
                    #             'vat_general_base':0,
                    #             'vat_general_tax':0,
                    #             'vat_additional_base':0,
                    #             'vat_additional_tax':0,
                    #         }
                    #     lines = [(0,0,line_dict)]
                    #     rec.write({'fbl_ids':lines})
                    # Si están en borrador, se añade como facturas con problemas
                    if order.state == 'draft':
                        line_dict = {
                                'name': order.name,
                                'invoice_id':order.id,
                                'partner_name':order.partner_id.name,
                            }
                        lines = [(0,0,line_dict)]
                        rec.write({'issue_invoice_ids':lines})
                retentions=self.env['account.wh.iva'].search([('state','not in',('cancel','draft')),('move_type','in',('in_invoice','in_refund')),('date','>=',self.period_start),('date','<=',self.period_end),('company_id','=',self.company_id.id)]).mapped('wh_lines')
                for rete in retentions:
                    multiplicador = 1 if rete.retention_id.move_type in ('in_invoice','out_invoice') else -1
                    line_dict = {           
                            'ret_amount':  abs(rete.ret_amount) * rete.retention_id.manual_currency_exchange_rate * multiplicador,
                            'rate_amount':  rete.rate_amount,
                            'name': rete.retention_id.number,
                            'retention_id':rete.retention_id.id,
                            'invoice_id':rete.invoice_id.id,
                            'retention_line_id':rete.id,
                            'date':rete.retention_id.date,
                        }
                    lines = [(0,0,line_dict)]
                    rec.write({'retention_ids':lines})
                if not line_dict:
                    raise UserError(_("Nada para declarar."))
    
    
    def print_xls_report(self):
        general_deducible_base = 0
        reduced_deducible_base = 0
        additional_deducible_base = 0
        general_deducible_tax = 0
        reduced_deducible_tax = 0
        additional_deducible_tax = 0
        general_no_deducible_base = 0
        reduced_no_deducible_base = 0
        additional_no_deducible_base = 0
        general_no_deducible_tax = 0
        reduced_no_deducible_tax = 0
        additional_no_deducible_tax = 0
        if self.type == 'sale':
            self.ensure_one()
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

            worksheet.merge_range('F4:H4', "-", header_merge_format)
            worksheet.merge_range(4, 3, 6, 10,  'LIBRO DE VENTAS', header_merge_format_titulo)
            worksheet.write(8, 5, "Desde:", header_merge_format)
            worksheet.write(8, 6, self.period_start, fecha)
            worksheet.write(8, 7, "Hasta: ", header_merge_format)
            worksheet.write(8, 8, self.period_end, fecha)

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
            worksheet.write(10, 15, "Base Imponible G", header_merge_format)
            worksheet.write(10, 16, "% Alicuota G", header_merge_format)
            worksheet.write(10, 17, "Impuesto IVA G", header_merge_format)
            worksheet.write(10, 18, "Base Imponible R", header_merge_format)
            worksheet.write(10, 19, "% Alícuota R", header_merge_format)
            worksheet.write(10, 20, "Impuesto IVA R", header_merge_format)
            worksheet.write(10, 21, "Base Imponible A", header_merge_format)
            worksheet.write(10, 22, "% Alícuota A", header_merge_format)
            worksheet.write(10, 23, "Impuesto IVA A", header_merge_format)
            worksheet.write(10, 24, "IVA Retenido por el Comprador", header_merge_format)
            worksheet.write(10, 25, "Comprobante de Retencion", header_merge_format)
            worksheet.write(10, 26, "IVA Percibido", header_merge_format)

            rows = 10
            cont = 0
            for s in self.fbl_ids.sorted(lambda r: (r.ctrl_number)):
                rows += 1            
                cont += 1

                # Oper N°
                worksheet.write(rows, 0, cont, header_data_format) 
                # Fecha de La Factura
                worksheet.write_datetime(rows,1, s.emission_date, fecha)
                # Rif o cedula
                worksheet.write(rows, 2, s.partner_vat, header_data_format)
                # Nombre o Razón Social
                worksheet.write(rows, 3, s.partner_name, header_data_format)
                # Número de Factura
                worksheet.write(rows, 4, s.name if not s.invoice_id.parent_id and not s.invoice_id.debit_origin_id else '-', header_data_format)
                # Serie
                worksheet.write(rows, 5, 'Serie '+s.invoice_id.account_serie.name if s.invoice_id.account_serie else '-', header_data_format)
                # Número de Control
                worksheet.write(rows, 6, s.ctrl_number if s.ctrl_number else '-', header_data_format)
                # Número de Nota Debito
                worksheet.write(rows, 7, s.name if s.debit_affected !='-' else '-', header_data_format)
                # Número Planilla de Exportación
                worksheet.write(rows, 8, s.invoice_id.num_import if s.invoice_id.num_import else '-', header_data_format)
                # Número de Expediente Exportacion
                worksheet.write(rows, 9, s.invoice_id.num_export if s.invoice_id.num_export else '-' , header_data_format)
                # Número de Nota Credito
                worksheet.write(rows, 10, s.name if s.credit_affected != '-' else '-', header_data_format)
                # Tipo de Transacción
                worksheet.write(rows, 11, s.type, header_data_format)
                # Número de Factura Afectada
                worksheet.write(rows, 12, s.affected_invoice if s.affected_invoice else '-', header_data_format)
                # Total Ventas Incluyendo el IVA
                worksheet.write(rows, 13, s.total_with_iva, currency_format)
                # Ventas Exentas o Exoneradas
                worksheet.write(rows,14, s.vat_exempt, currency_format)
                # Base Imponible
                worksheet.write(rows, 15, s.vat_general_base, currency_format)
                # % Alícuota
                worksheet.write(rows, 16, sum(s.invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general').mapped('amount')), currency_format)
                # Impuesto IVA
                worksheet.write(rows, 17, s.vat_general_tax, currency_format)
                # Base Imponible R
                worksheet.write(rows, 18, s.vat_reduced_base, currency_format)
                # % Alícuota R
                worksheet.write(rows, 19, sum(s.invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced').mapped('amount')), currency_format)
                # Impuesto IVA R
                worksheet.write(rows, 20, s.vat_reduced_tax, currency_format)
                # Base Imponible A
                worksheet.write(rows, 21, s.vat_additional_base, currency_format)
                # % Alícuota A
                worksheet.write(rows, 22, sum(s.invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional').mapped('amount')), currency_format)
                # Impuesto IVA A
                worksheet.write(rows, 23, s.vat_additional_tax, currency_format)
                # IVA Retenido por el Comprador
                worksheet.write(rows, 24, 0.00, currency_format)
                # Comprobante de Retencion
                worksheet.write(rows, 25, '-', header_data_format)
                # IVA Percibido
                worksheet.write(rows, 26, 0, currency_format)
                
            # # Recorrido de las Retenciones
            #retentions=self.env['account.wh.iva'].search([('state','not in',('cancel','draft')),('move_type','=','out_invoice'),('date','>=',self.period_start),('date','<=',self.period_end),('company_id','=',self.company_id.id)]).mapped('wh_lines')
            #for ret in retentions.sorted(lambda r: (r.retention_id.date, r.retention_id.id)):
            for ret in self.retention_ids.sorted(lambda r: (r.retention_id.date, r.retention_id.id)):
                rows += 1            
                cont += 1
                # Oper N°
                worksheet.write(rows, 0, cont, header_data_format)
                # Fecha de La Factura
                worksheet.write_datetime(rows,1, ret.retention_id.date, fecha)
                # Rif o cedula
                worksheet.write(rows, 2, ret.retention_id.partner_id.rif, header_data_format)
                # Nombre o Razón Social
                worksheet.write(rows, 3, ret.retention_id.partner_id.name, header_data_format)
                # Número de Factura
                worksheet.write(rows, 4, '-', header_data_format)
                # Serie
                worksheet.write(rows, 5, '-', header_data_format)
                # Número de Control
                worksheet.write(rows, 6, ret.invoice_id.nro_control if ret.invoice_id.nro_control else '-', header_data_format)
                # Número de Nota Debito
                worksheet.write(rows, 7, '-', header_data_format)
                # Número Planilla de Exportación
                worksheet.write(rows, 8, "-", header_merge_format)
                # Número de Expediente Exportacion
                worksheet.write(rows, 9, "-", header_merge_format)
                # Número de Nota Credito
                worksheet.write(rows, 10, '-', header_data_format)
                # Tipo de Transacción
                worksheet.write(rows, 11, '-', header_data_format)
                # Número de Factura Afectada
                worksheet.write(rows, 12, ret.invoice_id.name if ret.invoice_id.name else '-', header_data_format)
                # Total Ventas Incluyendo el IVA
                worksheet.write(rows, 13, 0.00, currency_format)
                # Ventas Exentas o Exoneradas
                worksheet.write(rows, 14, 0.00, currency_format)
                # Base Imponible
                worksheet.write(rows, 15, 0.00, currency_format)
                # % Alícuota
                worksheet.write(rows, 16, 0.00, currency_format)
                # Impuesto IVA
                worksheet.write(rows, 17, 0.00, currency_format)
                # Base Imponible R
                worksheet.write(rows, 18, 0.00, currency_format)
                # % Alícuota R
                worksheet.write(rows, 19, 0.00, currency_format)
                # Impuesto IVA R
                worksheet.write(rows, 20, 0.00, currency_format)
                # Base Imponible A
                worksheet.write(rows, 21, 0.00, currency_format)
                # % Alícuota A
                worksheet.write(rows, 22, 0.00, currency_format)
                # Impuesto IVA A
                worksheet.write(rows, 23, '-', header_data_format)
                # IVA Retenido por el Comprador
                worksheet.write(rows, 24, ret.ret_amount, currency_format)
                # Comprobante de Retencion
                worksheet.write(rows, 25, ret.retention_id.customer_doc_number, header_data_format)
                # IVA Percibido
                worksheet.write(rows, 26, 0, currency_format)
            
            #TOTALES        
            worksheet.write(rows+1, 12,'TOTALES', header_data_format)
            worksheet.write(rows+1, 13, self.total_with_iva, currency_format)           #Total Ventas Incluyendo el IVA
            worksheet.write(rows+1, 14, self.total_vat_exempt, currency_format)         #Ventas Internas No Gravadas
            worksheet.write(rows+1, 15, self.total_vat_general_base, currency_format)   #Base Imponible
            worksheet.write(rows+1, 16, '-', header_data_format)                        #alicuota
            worksheet.write(rows+1, 17, self.total_vat_general_tax, currency_format)    #Total Impuestos (General )
            worksheet.write(rows+1, 18, self.total_vat_reduced_base, currency_format)   #Base Imponible Reduced
            worksheet.write(rows+1, 19, '-', header_data_format)                        #alicuota Reduced
            worksheet.write(rows+1, 20, self.total_vat_reduced_tax, currency_format)    #Total Impuestos (Reducido) Reduced
            worksheet.write(rows+1, 21, self.total_vat_additional_base, currency_format)   #Base Imponible Additional
            worksheet.write(rows+1, 22, '-', header_data_format)                        #alicuota Additional
            worksheet.write(rows+1, 23, self.total_vat_additional_tax, currency_format)    #Total Impuestos ( Adicional) Additional
            worksheet.write(rows+1, 24, self.get_wh_sum, currency_format)               #IVA RETENIDO POR EL COMPRADOR
            worksheet.write(rows+1, 25, '-', header_data_format)                        #número de comprobante
            worksheet.write(rows+1, 26, 0.0 , currency_format)                          #IVA PERCIBIDO

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
            # TOTAL DE BASE IMPONIBLE
            R46 = self.total_vat_exempt + self.total_vat_general_base + self.total_vat_additional_base + self.total_vat_reduced_base
            worksheet.merge_range(rows+4, 14, rows+4, 15, self.total_vat_exempt, currency_format)#2
            worksheet.merge_range(rows+5, 14, rows+5, 15, 0.00, currency_format )#2
            worksheet.merge_range(rows+6, 14, rows+6, 15, self.total_vat_general_base, currency_format)#2
            worksheet.merge_range(rows+7, 14, rows+7, 15, self.total_vat_additional_base, currency_format)#2
            worksheet.merge_range(rows+8, 14, rows+8, 15, self.total_vat_reduced_base, currency_format)#2
            worksheet.merge_range(rows+9, 14, rows+9, 15, R46, currency_format)#2
            
            # Total de Impuestos
            R47 = self.total_vat_general_tax + self.total_vat_additional_tax + self.total_vat_reduced_tax
            worksheet.merge_range(rows+4, 16, rows+4, 17, '', header_data_format)#3
            worksheet.merge_range(rows+5, 16, rows+5, 17, '', header_data_format )#3
            worksheet.merge_range(rows+6, 16, rows+6, 17, self.total_vat_general_tax, currency_format)#3
            worksheet.merge_range(rows+7, 16, rows+7, 17, self.total_vat_additional_tax, currency_format)#3
            worksheet.merge_range(rows+8, 16, rows+8, 17, self.total_vat_reduced_tax, currency_format)#3
            worksheet.merge_range(rows+9, 16, rows+9, 17, R47, currency_format)#3

            worksheet.merge_range(rows+4, 19, rows+4, 20, '', header_data_format)#5
            worksheet.merge_range(rows+5, 19, rows+5, 20, '', header_data_format )#5
            worksheet.merge_range(rows+6, 19, rows+6, 20, self.get_wh_sum, currency_format)#5
            worksheet.merge_range(rows+7, 19, rows+7, 20, 0.00, currency_format)#5
            worksheet.merge_range(rows+8, 19, rows+8, 20, 0.00, currency_format)#5
            worksheet.merge_range(rows+9, 19, rows+9, 20, '', header_data_format)#5

            iva_percibido= self.total_vat_general_tax-self.get_wh_sum
            worksheet.merge_range(rows+4, 21, rows+4, 22,  '', header_data_format) #6
            worksheet.merge_range(rows+5, 21, rows+5, 22, '', header_data_format )#6
            worksheet.merge_range(rows+6, 21, rows+6, 22, 0.00, currency_format)#6
            worksheet.merge_range(rows+7, 21, rows+7, 22, 0.00, currency_format) #6
            worksheet.merge_range(rows+8, 21, rows+8, 22, 0.00, currency_format) #6
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
            worksheet.merge_range(rows+11, 19, rows+11, 20, 0.00, currency_format) #base imponible
            worksheet.merge_range(rows+11, 21, rows+11, 22, 0.00, currency_format) #debito fiscal

            #NO CONTRIBUYENTE
            worksheet.merge_range(rows+12, 19, rows+12, 20, '', header_data_format) #base imponible
            worksheet.merge_range(rows+12, 21, rows+12, 22, '', header_data_format) #debito fiscal
            
            workbook.close()
            out=base64.encodestring(fp.getvalue())
            self.write({
                'data': out,
            })
        if self.type=='purchase':
        
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
          
            worksheet.merge_range('F4:H4', "", header_merge_format)
            worksheet.merge_range(4, 3, 6, 10,  'LIBRO DE COMPRAS', header_merge_format)
            worksheet.write(8, 5, "Desde:", header_merge_format)
            worksheet.write(8, 6, self.period_start, fecha)
            worksheet.write(8, 7, "Hasta: ", header_merge_format)
            worksheet.write(8, 8, self.period_end, fecha)

            worksheet.merge_range(9, 12, 9, 16, 'COMPRAS INTERNAS O IMPORTACIONES', header_merge_format)
            worksheet.merge_range(9, 17, 9, 25, 'Impuestos Deducible', header_merge_format)
            worksheet.merge_range(9, 26, 9, 34, 'Impuestos no Deducible', header_merge_format)
            
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
            worksheet.write(10, 15, "Compras Exoneradas", header_merge_format)
            worksheet.write(10, 16, "Compras No sujetas", header_merge_format)
            # Deducible
            worksheet.write(10, 17, "Base Imponible Deducible G", header_merge_format)
            worksheet.write(10, 18, "% Alícuota Deducible G", header_merge_format)
            worksheet.write(10, 19, "Impuesto IVA Deducible G", header_merge_format)
            # Reducido
            worksheet.write(10, 20, "Base Imponible Deducible R", header_merge_format)
            worksheet.write(10, 21, "% Alícuota Deducible R", header_merge_format)
            worksheet.write(10, 22, "Impuesto IVA Deducible R", header_merge_format)
            # Adicional
            worksheet.write(10, 23, "Base Imponible Deducible A", header_merge_format)
            worksheet.write(10, 24, "% Alícuota Deducible A", header_merge_format)
            worksheet.write(10, 25, "Impuesto IVA Deducible A", header_merge_format)
            # No deducible
            # General
            worksheet.write(10, 26, "Base Imponible no deducible G", header_merge_format)
            worksheet.write(10, 27, "% Alícuota no deducible G", header_merge_format)
            worksheet.write(10, 28, "IVA no deducible G", header_merge_format)
            # Reducido
            worksheet.write(10, 29, "Base Imponible no deducible R", header_merge_format)
            worksheet.write(10, 30, "% Alícuota no deducible R", header_merge_format)
            worksheet.write(10, 31, "IVA no deducible R", header_merge_format)
            # Adicional
            worksheet.write(10, 32, "Base Imponible no deducible A", header_merge_format)
            worksheet.write(10, 33, "% Alícuota no deducible A", header_merge_format)
            worksheet.write(10, 34, "IVA no deducible A", header_merge_format)
            # Retenciones
            worksheet.write(10, 35, "IVA retenido (al Vendedor)", header_merge_format)
            worksheet.write(10, 36, "% Retención", header_merge_format)
            worksheet.write(10, 37, "Comprobante. de Retención", header_merge_format)

            rows = 10
            cont = 0
            for u in self.fbl_ids:
                rows += 1
                cont += 1
                #Oper. N°
                worksheet.write(rows, 0, cont, header_data_format)
                #Fecha de la Factura
                worksheet.write_datetime(rows,1, u.emission_date, fecha)
                #RIF o Cedula
                worksheet.write(rows,2, u.partner_vat if u.partner_vat else '-', header_data_format)
                #Nombre o Razón Social
                worksheet.write(rows,3, u.partner_name, header_data_format)
                #Serie
                worksheet.write(rows,4, '-', header_data_format)
                #Tipo de Prov.
                worksheet.write(rows,5, u.invoice_id.partner_id.residence_type if u.invoice_id.partner_id.residence_type else '-', header_data_format) 
                # Numero de Factura
                worksheet.write(rows,6, u.invoice_id.vendor_invoice_number if not u.invoice_id.parent_id and not u.invoice_id.debit_origin_id else '-', header_data_format)
                #Núm. Control
                worksheet.write(rows,7, u.ctrl_number, header_data_format)
                # Número Planilla de Importación
                worksheet.write(rows,8, u.invoice_id.num_import if u.invoice_id.num_import else '-', header_data_format)
                #Número de Expediente Importación
                worksheet.write(rows,9, u.invoice_id.num_export if u.invoice_id.num_export else '-', header_data_format)
                #Número nota de débito
                worksheet.write(rows,10, u.invoice_id.vendor_invoice_number if u.invoice_id.debit_origin_id else '-', header_data_format)
                #Número nota de credito
                worksheet.write(rows,11, u.invoice_id.vendor_invoice_number if u.invoice_id.move_type == 'in_refund' else '-', header_data_format)
                # Número factura afectada
                worksheet.write(rows,12, u.invoice_id.debit_origin_id.vendor_invoice_number if u.invoice_id.debit_origin_id else u.invoice_id.parent_id.vendor_invoice_number if u.invoice_id.parent_id else '-', header_data_format)
                # Total Compras Incluyendo IVA
                worksheet.write(rows,13, u.total_with_iva, currency_format)
                #"Compras exentas               
                worksheet.write(rows,14, u.vat_exempt, currency_format)
                # Compras Exoneradas
                worksheet.write(rows,15, '-', header_data_format)
                #Compras No sujetas
                worksheet.write(rows,16, '-', header_data_format)
                #IVA NO DEDUCIBLE
                if not u.invoice_id.deductible:
                    # totales NO deducible
                    general_no_deducible_base += u.vat_general_base
                    reduced_no_deducible_base += u.vat_reduced_base
                    additional_no_deducible_base += u.vat_additional_base
                    general_no_deducible_tax += u.vat_general_tax
                    reduced_no_deducible_tax += u.vat_reduced_tax
                    additional_no_deducible_tax += u.vat_additional_tax
                    #Base Imponible Deducible G"
                    worksheet.write(rows,17, u.vat_general_base, currency_format)
                    #% Alícuota Deducible G"
                    worksheet.write(rows,18, sum(u.invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general').mapped('amount')), currency_format)
                    #Impuesto IVA Deducible G"
                    worksheet.write(rows,19, u.vat_general_tax, currency_format)
                    # Reducido
                    #Base Imponible Deducible R"
                    worksheet.write(rows,20, u.vat_reduced_base, currency_format)
                    #% Alícuota Deducible R"
                    worksheet.write(rows,21, sum(u.invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced').mapped('amount')), currency_format)
                    #Impuesto IVA Deducible R"
                    worksheet.write(rows,22, u.vat_reduced_tax, currency_format)
                    # Adicional
                    #Base Imponible Deducible A"
                    worksheet.write(rows,23, u.vat_additional_base, currency_format)
                    #% Alícuota Deducible A"
                    worksheet.write(rows,24, sum(u.invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional').mapped('amount')), currency_format)
                    #Impuesto IVA Deducible A"
                    worksheet.write(rows,25, u.vat_additional_tax, currency_format)

                    # NO deducible
                    #Base Imponible no deducible G"
                    worksheet.write(rows,26, 0.00, currency_format)
                    #% Alícuota No deducible G"
                    worksheet.write(rows,27, 0.00, currency_format)
                    #IVA no deducible G
                    worksheet.write(rows,28, 0.00, currency_format)
                    # Reducido
                    #Base Imponible no deducible R"
                    worksheet.write(rows,29, 0.00, currency_format)
                    #% Alícuota No deducible R"
                    worksheet.write(rows,30, 0.00, currency_format)
                    #IVA no deducible R"
                    worksheet.write(rows,31, 0.00, currency_format)
                    # Adicional
                    #Base Imponible no deducible A"
                    worksheet.write(rows,32, 0.00, currency_format)
                    #% Alícuota No deducible A"
                    worksheet.write(rows,33, 0.00, currency_format)
                    #IVA no deducible A"
                    worksheet.write(rows,34, 0.00, currency_format)
                # IVA DEDUCIBLE
                if u.invoice_id.deductible:
                    # totales deducible
                    general_deducible_base += u.vat_general_base
                    reduced_deducible_base += u.vat_reduced_base
                    additional_deducible_base += u.vat_additional_base
                    general_deducible_tax += u.vat_general_tax
                    reduced_deducible_tax += u.vat_reduced_tax
                    additional_deducible_tax += u.vat_additional_tax
                    #Base Imponible Deducible G"
                    worksheet.write(rows,17, 0.00, currency_format)
                    #% Alícuota Deducible G"
                    worksheet.write(rows,18, 0.00, currency_format)
                    #Impuesto IVA Deducible G"
                    worksheet.write(rows,19, 0.00, currency_format)
                    # Reducido
                    #Base Imponible Deducible R"
                    worksheet.write(rows,20, 0.00, currency_format)
                    #% Alícuota Deducible R"
                    worksheet.write(rows,21, 0.00, currency_format)
                    #Impuesto IVA Deducible R"
                    worksheet.write(rows,22, 0.00, currency_format)
                    # Adicional
                    #Base Imponible Deducible A"
                    worksheet.write(rows,23, 0.00, currency_format)
                    #% Alícuota Deducible A"
                    worksheet.write(rows,24, 0.00, currency_format)
                    #Impuesto IVA Deducible A"
                    worksheet.write(rows,25, 0.00, currency_format)

                    # NO deducible
                    #Base Imponible no deducible G"
                    worksheet.write(rows,26, u.vat_general_base, currency_format)
                    #% Alícuota No deducible G"
                    worksheet.write(rows,27, sum(u.invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general').mapped('amount')), currency_format)
                    #IVA no deducible G
                    worksheet.write(rows,28, u.vat_general_tax, currency_format)
                    # Reducido
                    #Base Imponible no deducible R"
                    worksheet.write(rows,29, u.vat_reduced_base, currency_format)
                    #% Alícuota No deducible R"
                    worksheet.write(rows,30, sum(u.invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced').mapped('amount')), currency_format)
                    #IVA no deducible R"
                    worksheet.write(rows,31, u.vat_reduced_tax, currency_format)
                    # Adicional
                    #Base Imponible no deducible A"
                    worksheet.write(rows,32, u.vat_additional_base, currency_format)
                    #% Alícuota No deducible A"
                    worksheet.write(rows,33, sum(u.invoice_id.invoice_line_ids.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional').mapped('amount')), currency_format)
                    #IVA no deducible A"
                    worksheet.write(rows,34, u.vat_additional_tax, currency_format)

                #IVA retenido (al Vendedor)
                worksheet.write(rows,35, '-', currency_format)
                #% Retención
                worksheet.write(rows,36, '-', currency_format)
                #Comprobante. de Retención
                worksheet.write(rows,37, '-', currency_format)
                    
            #linea de las retenciones
            #retentions=self.env['account.wh.iva'].search([('state','not in',('cancel','draft')),('move_type','in',('in_invoice','in_refund')),('date','>=',self.period_start),('date','<=',self.period_end),('company_id','=',self.company_id.id)]).mapped('wh_lines')
            for ret in self.retention_ids.sorted(lambda r: (r.retention_id.date, r.retention_id.id)):
                rows += 1
                cont += 1
                #Oper. N°
                worksheet.write(rows, 0, cont, header_data_format)
                #Fecha de la Factura
                worksheet.write_datetime(rows,1, ret.retention_id.date, fecha)#Fecha de la retención
                #RIF o Cedula
                worksheet.write(rows,2, ret.retention_id.partner_id.rif, header_data_format)#RIF
                #Nombre o Razón Social
                worksheet.write(rows,3, ret.retention_id.partner_id.name, header_data_format)#Nombre o Razón social
                #Serie
                worksheet.write(rows,4, '-',header_data_format)
                #Tipo de Prov.
                worksheet.write(rows,5, ret.retention_id.partner_id.residence_type, header_data_format)#Tipo de Proveedor
                # Numero de Factura
                worksheet.write(rows,6, '-', header_data_format)#nmero de factura
                #Núm. Control
                worksheet.write(rows,7, ret.invoice_id.nro_control, header_data_format)#Número de Control de Factura
                # Número Planilla de Importación
                worksheet.write(rows,8, '-', header_data_format)#Número de Planilla de Importación
                #Número de Expediente Importación
                worksheet.write(rows,9, '-', header_data_format)
                #Número nota de débito
                worksheet.write(rows,10, '-', header_data_format)
                #Número nota de credito
                worksheet.write(rows,11, '-', header_data_format)
                # Número factura afectada
                worksheet.write(rows,12, ret.invoice_id.vendor_invoice_number, header_data_format)
                # Total Compras Incluyendo IVA
                worksheet.write(rows,13, '-', header_data_format)
                #"Compras exentas               
                worksheet.write(rows,14, '-', header_data_format)
                # Compras Exoneradas
                worksheet.write(rows,15, '-', header_data_format)
                #Compras No sujetas
                worksheet.write(rows,16, '-', header_data_format)
                #Base Imponible Deducible G"
                worksheet.write(rows,17, '-', header_data_format)
                #% Alícuota Deducible G"
                worksheet.write(rows,18, '-', header_data_format)
                #Impuesto IVA Deducible G"
                worksheet.write(rows,19, '-', header_data_format)
                #Base Imponible Deducible R"
                worksheet.write(rows,20, '-', header_data_format)
                #% Alícuota Deducible R"
                worksheet.write(rows,21, '-', header_data_format)
                #Impuesto IVA Deducible R"
                worksheet.write(rows,22, '-', header_data_format)
                #Base Imponible Deducible A"
                worksheet.write(rows,23, '-', header_data_format)
                #% Alícuota Deducible A"
                worksheet.write(rows,24, '-', header_data_format)
                #Impuesto IVA Deducible A"
                worksheet.write(rows,25, '-', header_data_format)
                #Base Imponible no deducible G"
                worksheet.write(rows,26, '-', header_data_format)
                #% Alícuota No deducible G"
                worksheet.write(rows,27, '-', header_data_format)
                #IVA no deducible G
                worksheet.write(rows,28, '-', header_data_format)
                #Base Imponible no deducible R"
                worksheet.write(rows,29, '-', header_data_format)
                #% Alícuota No deducible R"
                worksheet.write(rows,30, '-', header_data_format)
                #IVA no deducible R"
                worksheet.write(rows,31, '-', header_data_format)
                #Base Imponible no deducible A"
                worksheet.write(rows,32, '-', header_data_format)
                #% Alícuota No deducible A"
                worksheet.write(rows,33, '-', header_data_format)
                #IVA no deducible A"
                worksheet.write(rows,34, '-', header_data_format)
                #IVA retenido (al Vendedor)
                worksheet.write(rows,35, ret.ret_amount, currency_format)
                #% Retención
                worksheet.write(rows,36, ret.rate_amount, currency_format)
                #Comprobante. de Retención
                worksheet.write(rows,37, ret.retention_id.number if ret.retention_id.move_type == 'in_refund' else ret.retention_id.number, currency_format)

            worksheet.write(rows+1,13, self.total_with_iva, currency_format)
            worksheet.write(rows+1,14, self.total_vat_exempt, currency_format)
            worksheet.write(rows+1,15, 0.0, currency_format)
            worksheet.write(rows+1,16, 0.0, currency_format)                         
            #DEDUCIBLE INICIO
            #GENERAL
            worksheet.write(rows+1,17, general_no_deducible_base, currency_format)
            worksheet.write(rows+1,18, 0.0, currency_format)
            worksheet.write(rows+1,19, general_no_deducible_tax, currency_format)
            # REDUCIDO
            worksheet.write(rows+1,20, reduced_no_deducible_base, currency_format)
            worksheet.write(rows+1,21, 0.0, currency_format)
            worksheet.write(rows+1,22, reduced_no_deducible_tax, currency_format)
            # ADICIONAL
            worksheet.write(rows+1,23, additional_no_deducible_base, currency_format)
            worksheet.write(rows+1,24, 0.0, currency_format)
            worksheet.write(rows+1,25, additional_no_deducible_tax, currency_format)
            #DEDUCIBLE FIN
            #NO DEDUCIBLE INICIO
            # GENERAL
            worksheet.write(rows+1,26, general_deducible_base, currency_format)
            worksheet.write(rows+1,27, 0.0, currency_format)
            worksheet.write(rows+1,28, general_deducible_tax, currency_format)
            # REDUCIDO
            worksheet.write(rows+1,29, reduced_deducible_base, currency_format)
            worksheet.write(rows+1,30, 0.0, currency_format)
            worksheet.write(rows+1,31, reduced_deducible_tax, currency_format)
            # ADICIONAL
            worksheet.write(rows+1,32, additional_deducible_base, currency_format)
            worksheet.write(rows+1,33, 0.0, currency_format)
            worksheet.write(rows+1,34, additional_deducible_tax, currency_format)
            #MO DEDUCIBLE FIN
            # Total Retenido
            worksheet.write(rows+1,35, self.get_wh_sum, currency_format)
            # % Retención
            worksheet.write(rows+1,36, '-', currency_format)

            #Se definen las variables dependientes de otras

            #TABLA ADICIONAL
            #ESTRUCTURA DE LA TABLA
            #COLUMNAS
            worksheet.write(rows+3, 18,'', header_data_format)#1
            worksheet.merge_range(rows+3, 19, rows+3, 20,  'Base imponible', header_data_format) #2
            worksheet.write(rows+3, 21,'', header_data_format) #3
            worksheet.merge_range(rows+3, 22, rows+3, 23,  'Crédito Fiscal', header_data_format)  #4
            worksheet.merge_range(rows+3, 24, rows+3, 25,  'IVA Retenido (al Vendedor)', header_data_format)#5

            #FILAS
            worksheet.merge_range(rows+4, 12, rows+4, 17,  'Total : Compras Exentas y/o sin derecho a crédito fiscal', header_data_format)
            worksheet.merge_range(rows+5, 12, rows+5, 17,  'Compras Importación afectadas solo Alicuota General', header_data_format)
            worksheet.merge_range(rows+6, 12, rows+6, 17,  'Compras Importación Afectas en Alicuota General + Adicional', header_data_format)
            worksheet.merge_range(rows+7, 12, rows+7, 17,  'Compras Importación Afectas en Alicuota Reducida', header_data_format)
            worksheet.merge_range(rows+8, 12, rows+8, 17,  'Compras Internas Afectas en Alicuota General + Adicional', header_data_format)
            worksheet.merge_range(rows+9, 12, rows+9, 17,  'Compras Internas Afectas en Alicuota Reducida', header_data_format)
            worksheet.merge_range(rows+10, 12, rows+10, 17,'Compras Internas Afectas solo Alicuota General', header_data_format)
            worksheet.merge_range(rows+11, 12, rows+11, 17,'TOTAL', header_data_format)

            worksheet.write(rows+4, 18,'30', header_data_format)                 #1
            worksheet.write(rows+5, 18,'31', header_data_format)                 #1
            worksheet.write(rows+6, 18,'312', header_data_format)                #1
            worksheet.write(rows+7, 18,'313', header_data_format)                #1
            worksheet.write(rows+8, 18,'332', header_data_format)                #1
            worksheet.write(rows+9, 18,'333', header_data_format)                #1
            worksheet.write(rows+10, 18,'33', header_data_format)                #1
            worksheet.write(rows+11, 18,'35', header_data_format)                #1


            worksheet.write(rows+4,  21,'', header_data_format)                  #3
            worksheet.write(rows+5,  21,'32', header_data_format)                #3
            worksheet.write(rows+6,  21,'322', header_data_format)               #3
            worksheet.write(rows+7,  21,'323', header_data_format)               #3
            worksheet.write(rows+8,  21,'342', header_data_format)               #3
            worksheet.write(rows+9,  21,'343', header_data_format)               #3
            worksheet.write(rows+10, 21,'34', header_data_format)                #3
            worksheet.write(rows+11, 21,'36', header_data_format)                #3

            # Base Imponible
            R35 = self.total_vat_exempt + self.total_vat_general_base + self.total_vat_additional_base + self.total_vat_reduced_base - general_deducible_base - reduced_deducible_base - additional_deducible_base
            worksheet.merge_range(rows+4, 19, rows+4, 20, self.total_vat_exempt, currency_format)     #2
            worksheet.merge_range(rows+5, 19, rows+5, 20, 0, currency_format)     #2
            worksheet.merge_range(rows+6, 19, rows+6, 20, 0, currency_format)     #2
            worksheet.merge_range(rows+7, 19, rows+7, 20, 0, currency_format)     #2
            worksheet.merge_range(rows+8, 19, rows+8, 20, self.total_vat_additional_base - additional_deducible_base, currency_format)     #2
            worksheet.merge_range(rows+9, 19, rows+9, 20, self.total_vat_reduced_base - reduced_deducible_base, currency_format)     #2
            worksheet.merge_range(rows+10, 19, rows+10, 20, self.total_vat_general_base - general_deducible_base, currency_format)   #2
            worksheet.merge_range(rows+11, 19, rows+11, 20, R35, currency_format)   #2

            # Impuestos
            R36 = self.total_vat_general_tax + self.total_vat_additional_tax + self.total_vat_reduced_tax - general_deducible_tax - reduced_deducible_tax - additional_deducible_tax
            worksheet.merge_range(rows+4, 22, rows+4, 23, 0.0, currency_format)  #4
            worksheet.merge_range(rows+5, 22, rows+5, 23, 0, currency_format)     #4
            worksheet.merge_range(rows+6, 22, rows+6, 23, 0, currency_format)     #4
            worksheet.merge_range(rows+7, 22, rows+7, 23, 0, currency_format)     #4
            worksheet.merge_range(rows+8, 22, rows+8, 23, self.total_vat_additional_tax - additional_deducible_tax, currency_format)     #4
            worksheet.merge_range(rows+9, 22, rows+9, 23, self.total_vat_reduced_tax - reduced_deducible_tax, currency_format)     #4
            worksheet.merge_range(rows+10, 22, rows+10, 23, self.total_vat_general_tax - general_deducible_tax, currency_format)   #4
            worksheet.merge_range(rows+11, 22, rows+11, 23, R36, currency_format)   #4

            worksheet.merge_range(rows+4, 24, rows+4, 25,  0.0, currency_format) #5
            worksheet.merge_range(rows+5, 24, rows+5, 25,  0.0, currency_format) #5
            worksheet.merge_range(rows+6, 24, rows+6, 25,  0.0, currency_format) #5
            worksheet.merge_range(rows+7, 24, rows+7, 25,  0.0, currency_format) #5
            worksheet.merge_range(rows+8, 24, rows+8, 25,  0.0, currency_format) #5
            worksheet.merge_range(rows+9, 24, rows+9, 25,  0.0, currency_format) #5
            worksheet.merge_range(rows+10, 24, rows+10, 25, self.get_wh_sum, currency_format)  #5
            worksheet.merge_range(rows+11, 24, rows+11, 25, self.get_wh_sum, currency_format)  #5

            #ULTIMA TABLA
            #COLUMNAS

            worksheet.merge_range(rows+13, 21, rows+13, 25, 'Resumen Tasa General', header_data_format)
            worksheet.write(rows+14,  21,'Tasa', header_data_format)
            worksheet.merge_range(rows+14, 22, rows+14, 23, 'Base Imponible', header_data_format)
            worksheet.merge_range(rows+14, 24, rows+14, 25, 'Debito Fiscal', header_data_format)

            worksheet.write(rows+15,  21,'8%', header_data_format)
            worksheet.merge_range(rows+15, 22, rows+15, 23, self.total_vat_reduced_base - reduced_deducible_base, currency_format)
            worksheet.merge_range(rows+15, 24, rows+15, 25, self.total_vat_reduced_tax - reduced_deducible_tax, currency_format)

            worksheet.write(rows+16,  21,'16%', header_data_format)
            worksheet.merge_range(rows+16, 22, rows+16, 23, self.total_vat_general_base - general_deducible_base, currency_format)
            worksheet.merge_range(rows+16, 24, rows+16, 25, self.total_vat_general_tax - general_deducible_tax, currency_format)

            worksheet.write(rows+17,  21,'22%', header_data_format)
            worksheet.merge_range(rows+17, 22, rows+17, 23, self.total_vat_additional_base - additional_deducible_base, currency_format)
            worksheet.merge_range(rows+17, 24, rows+17, 25, self.total_vat_additional_tax - additional_deducible_tax, currency_format)
            
            workbook.close()
            out=base64.encodestring(fp.getvalue())
            self.write({
                'data': out,
            })