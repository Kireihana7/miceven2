# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError
import base64
from odoo.tools.image import image_data_uri
 
class AccountPaymentMultiCompany(models.Model):
    _name = "account.payment.multi.company"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Multi Company payment "
    
    name = fields.Char(string="Nombre",default="/",readonly=True)  
    state = fields.Selection([
        ('cancel', 'Cancelado'),
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('validate', 'Enviado'),
        ('done', 'Recibido'),
        ], 'Estatus', default='draft',  required=True, readonly=True, tracking=True)
    posted_before = fields.Boolean(string="Confirmado",default=False)
    # Fechas
    confirm_date = fields.Date(string="Fecha de Confirmación",copy=False,readonly=True)
    validate_date = fields.Date(string="Fecha de Envío",copy=False,readonly=True)
    done_date = fields.Date(string="Fecha de Recepción",copy=False,readonly=True)
    # Compañías
    company_id_to   = fields.Many2one('res.company',string="Compañía")
    company_id_from = fields.Many2one('res.company',string="Compañía")  
    # Diarios de los Pagos
    journal_id_to = fields.Many2one('account.journal', string='Diario')
    journal_id_from = fields.Many2one('account.journal', string='Diario')
    
    # Montos
    amount = fields.Float('Monto',readonly=True,compute="_compute_amount_ref",store=True)
    amount_ref = fields.Float('Monto Ref',compute="_compute_amount_ref",store=True,readonly=True)
    #rate = fields.Float(string="Tasa",default=lambda self: self.env.company.currency_id.parent_id.rate)
    
    # Monedas
    currency_id = fields.Many2one('res.currency',string="Moneda",compute="_compute_currencys",store=True)
    currency_id_ref = fields.Many2one('res.currency',string="Moneda",compute="_compute_currencys",store=True)
    # Pagos
    payment_to = fields.One2many('account.payment','other_company_payment_id_to',string="Pago",readonly=False,copy=False)

    payment_from = fields.One2many('account.payment','other_company_payment_id_from',string="Pago",readonly=False,copy=False)
    
    # Facturación
    invoice_to = fields.Many2one('account.move',string="Asiento",readonly=True,copy=False)
    invoice_from = fields.Many2one('account.move',string="Asiento",readonly=True,copy=False)

    # Contador de Pagos
    payment_id_to_count = fields.Integer("Pagos Origen", compute='_compute_payment_count')
    payment_id_from_count = fields.Integer("Pagos Destino", compute='_compute_payment_count')


    @api.depends('payment_to')
    def _compute_amount_ref(self):
        for rec in self:
            rec.amount = sum(rec.payment_to.filtered(lambda x: x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(rec.payment_to.filtered(lambda x: x.currency_id != x.company_id.currency_id).mapped('amount_ref'))
            rec.amount_ref = sum(rec.payment_to.filtered(lambda x: x.currency_id != x.company_id.currency_id).mapped('amount')) + sum(rec.payment_to.filtered(lambda x: x.currency_id == x.company_id.currency_id).mapped('amount_ref'))

    @api.depends('journal_id_to','journal_id_from')
    def _compute_currencys(self):
        for rec in self:
            rec.currency_id = rec.journal_id_to.currency_id if rec.journal_id_to.currency_id else rec.company_id_to.currency_id
            rec.currency_id_ref = rec.journal_id_from.currency_id if rec.journal_id_from.currency_id else rec.company_id_from.currency_id
    
    @api.model    
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('other.multicompany.seq')
        vals.update({
            'name': name
            })
        res = super(AccountPaymentMultiCompany, self).create(vals)
        return res   

    @api.constrains('journal_id_to','journal_id_from')
    def _constrains_journals(self):
        for rec in self:
            if rec.journal_id_to == rec.journal_id_from:
                raise UserError('No puedes seleccionar el mismo diario en Origen y Destino')

    @api.constrains('company_id_to','company_id_from')
    def _constrains_company_id(self):
        for rec in self:
            if rec.company_id_to == rec.company_id_from:
                raise UserError('No puedes seleccionar la misma compañía en Origen y Destino')
    # Primer botón
    def button_confirm(self):
        for rec in self:
            # Cancela los Pagos de Origen y crea los de Destino
            if len(rec.payment_to.filtered(lambda x:x.currency_id != (rec.journal_id_to.currency_id if rec.journal_id_to.currency_id else rec.company_id.currency_id))) > 0:
                raise UserError('La moneda de los Pagos debe ser igual que la del diario a realizar')
            for pay in rec.payment_to:
                pay.action_draft()
                pay.action_cancel()
                creado = self.env['account.payment'].create(self.payment_dict_from(pay))
            rec.state='confirm'
            rec.confirm_date = fields.Date.today()
            rec.posted_before = True
    # Segundo botón
    def button_validate(self):
        for rec in self:
            # Publica los Pagos nuevos
            for pay in rec.payment_from:
                if pay.state=='draft':
                    pay.action_post()
            rec.state='validate'
            rec.validate_date = fields.Date.today()

    # Tercer Botón
    def button_done(self):
        for rec in self:
            # Crea los dos Asiento, Origen y destino
            rec.facturar_to()
            rec.facturar_from()
            #Publica los asientos creados
            rec.invoice_to.action_post()
            rec.invoice_from.action_post()
            rec.state='done'
            rec.done_date = fields.Date.today()

    # Botón Cancelar
    def button_cancel(self):
        for rec in self:
            rec.state='cancel'

    # Valores para los Pagos
    def payment_dict_from(self,pay):
        return {
            'payment_type':pay.payment_type,
            'partner_type':pay.partner_type,
            'amount':pay.amount,
            'payment_reg':pay.payment_reg,
            'company_id':self.company_id_from.id,
            'journal_id':self.journal_id_from.id,
            'ref':pay.ref,
            'active_manual_currency_rate':pay.active_manual_currency_rate,
            'manual_currency_exchange_rate': pay.manual_currency_exchange_rate,
            'partner_id':pay.partner_id.id,
            'destination_account_id':pay.partner_id.with_context(force_company=self.company_id_from.id).with_company(self.company_id_from).property_account_payable_id.id,
            'other_company_payment_id_from':self.id,
        }

    # Valores para el asiento
    def create_invoice(self,currency_id,partner_id,journal_id,company_id):
        return{
            "partner_id": partner_id.id,
            "partner_shipping_id": partner_id.id,
            "journal_id": journal_id.id,
            "currency_id": currency_id.id,
            "invoice_date": fields.Date.today(),
            "company_id": company_id.id,
            "move_type": 'entry',
            "invoice_payment_term_id": False,
            'apply_manual_currency_exchange':True,
            'manual_currency_exchange_rate':self.env.company.currency_id.parent_id.rate,
            'other_company_payment_id':self.id,
        }

    def create_lineas_vals(self,invoice_id,company_id,origen,currency_id,amount,amount_currency,account,partner):
        return {
            'debit': amount if origen == 'debit' else 0.0,
            'credit': amount if origen == 'credit' else 0.0,
            'balance': amount if origen=='debit' else -amount,
            'amount_currency': amount_currency if origen =='debit'else -amount_currency,
            'currency_id':currency_id.id,
            'move_id': invoice_id.id,
            'quantity':1,
            "account_id": account.id,
            'partner_id':partner.id,
        }
    # Asento Origen
    def facturar_to(self):
        for rec in self:
            if not rec.company_id_to.account_intercompany_id:
                raise UserError(('Debe configurar la cuenta intercompañía en %s') % (rec.company_id_to.name))
            journal_id = rec.journal_id_to
            partner_id = rec.company_id_from.partner_id
            currency_id = rec.currency_id
            amount = rec.amount
            amount_currency = rec.amount_ref
            account = rec.company_id_to.account_intercompany_id
            invoice_id = self.env["account.move"].sudo().create(rec.create_invoice(currency_id,partner_id,journal_id,rec.company_id_to))
            vals = rec.create_lineas_vals(invoice_id,rec.company_id_to,'credit',currency_id,amount,amount_currency,account,partner_id)
            invoice_id.line_ids.with_context(check_move_validity=False).sudo().create(vals)
            for pay in rec.payment_to:
                amount = pay.amount if pay.currency_id == pay.company_id.currency_id else pay.amount_ref
                amount_currency = pay.amount_ref if pay.currency_id == pay.company_id.currency_id else pay.amount
                account = pay.partner_id.with_context(force_company=self.company_id_to.id).with_company(self.company_id_to).property_account_payable_id
                partner_id = pay.partner_id
                vals = rec.create_lineas_vals(invoice_id,rec.journal_id_to,'debit',currency_id,amount,amount_currency,account,partner_id)
                invoice_id.line_ids.with_context(check_move_validity=False).sudo().create(vals)
            rec.write({"invoice_to": invoice_id.id})

    # Asento Destino
    def facturar_from(self):
        for rec in self:
            if not rec.company_id_from.account_intercompany_id:
                raise UserError(('Debe configurar la cuenta intercompañía en %s') % (rec.company_id_from.name))
            journal_id = rec.journal_id_from
            partner_id = rec.company_id_to.partner_id
            currency_id = rec.currency_id_ref
            amount = rec.amount
            amount_currency = rec.amount_ref
            account = rec.company_id_from.account_intercompany_id
            invoice_id = self.env["account.move"].sudo().create(rec.create_invoice(currency_id,partner_id,journal_id,rec.company_id_from))
            vals = rec.create_lineas_vals(invoice_id,rec.company_id_from,'debit',currency_id,amount,amount_currency,account,partner_id)
            invoice_id.line_ids.with_context(check_move_validity=False).sudo().create(vals)
            for pay in rec.payment_to:
                amount = pay.amount if pay.currency_id == pay.company_id.currency_id else pay.amount_ref
                amount_currency = pay.amount_ref if pay.currency_id == pay.company_id.currency_id else pay.amount
                account = pay.partner_id.with_context(force_company=self.company_id_from.id).with_company(self.company_id_from).property_account_payable_id
                partner_id = pay.partner_id
                vals = rec.create_lineas_vals(invoice_id,rec.company_id_from,'credit',currency_id,amount,amount_currency,account,partner_id)
                invoice_id.line_ids.with_context(check_move_validity=False).sudo().create(vals)
            rec.write({"invoice_from": invoice_id.id})
    
    def get_url_qr(self):
        for rec in self:
            parameter_base_web=self.env['ir.config_parameter'].sudo().search([('key','=','web.base.url')]).value
            db=rec._cr.dbname
            
            link = '%s/web?db=%s#id=%s&view_type=form&model=%s&cids=%s' % (parameter_base_web, db, rec.id,rec._name,self.env.company.id)
            param= {
                    'barcode_type': 'QR',
                    'width': 84,
                    'height': 84,
                    'humanreadable': 1,
                    'value': link,
                }
            barcode = self.env['ir.actions.report'].barcode(**param)
            return image_data_uri(base64.b64encode(barcode))

    def show_payment_id_to(self):
        return {
            'name': _('Pagos'),
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'view_id': False,
            'views': [(self.env.ref('account.view_account_supplier_payment_tree').id, 'tree')],
            'type': 'ir.actions.act_window',
            'domain': [('other_company_payment_id_to', '=', self.id)],
            'context': {'create': False},
        }

    def show_payment_id_from(self):
        return {
            'name': _('Pagos'),
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'view_id': False,
            'views': [(self.env.ref('account.view_account_supplier_payment_tree').id, 'tree')],
            'type': 'ir.actions.act_window',
            'domain': [('other_company_payment_id_from', '=', self.id)],
            'context': {'create': False},
        }

    def _compute_payment_count(self):
        for rec in self:
            rec.payment_id_to_count = len(rec.payment_to)
            rec.payment_id_from_count = len(rec.payment_from)

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft','cancel'):
                raise UserError('No puedes borrar un traslado que esté confirmado')
            if rec.posted_before:
                raise UserError('No puedes borrar un traslado que estuvo confirmado')
        res = super(AccountPaymentMultiCompany, self).unlink()