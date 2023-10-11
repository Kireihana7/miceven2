# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class AccountPaymentFastLine(models.Model):
    _name = 'account.payment.fast.line'
    _description = 'Pago Rapido Linea'

    fast_payment = fields.Many2one('account.payment.fast',default='Pago Rápido')
    name = fields.Char(string="Descripción",required=True)
    referencia = fields.Char(string="Referencia")
    amount = fields.Float(string="Monto USD",digits=(20,4))
    amount_bs = fields.Float(string="Monto VED",digits=(20,4))
    journal_id = fields.Many2one('account.journal',string="Diario",domain=[('type','in',('bank','cash'))],required=True)
    rate = fields.Float(string="Tasa",default=lambda self: self.env.company.currency_id.parent_id.rate,digits=(20,4))
    currency_id = fields.Many2one(related="journal_id.currency_id",store=True,string="Moneda")
    user_id = fields.Many2one(related="fast_payment.user_id",store=True)
    partner_id = fields.Many2one('res.partner',string="Cliente",required=True)
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    payment_id = fields.Many2one('account.payment',string="Pago Creado",readonly=True)
    sale_id = fields.Many2one('sale.order',string="Venta")
    invoice_id = fields.Many2one('account.move',string="Factura")


    @api.constrains("rate", "amount","amount_bs")
    def _check_floats(self):
        for rec in self:
            if rec.rate <= 0 or rec.amount <=0 or rec.amount_bs <=0:
                raise ValidationError('Los números deben ser mayor a cero')

    def payment_dict(self):
        return {
            'payment_type':'inbound',
            'partner_type':'customer',
            'amount':self.amount if self.currency_id == self.company_id.currency_id or not self.currency_id else self.amount_bs,
            'payment_reg':fields.Date.today(),
            'company_id':self.company_id.id,
            'journal_id':self.journal_id.id,
            'ref':self.name,
            'ref_bank':self.referencia,
            'active_manual_currency_rate':True,
            'manual_currency_exchange_rate': self.rate,
            'partner_id':self.partner_id.id,
            'destination_account_id':self.partner_id.property_account_receivable_id.id,
            'account_payment_fast':self.fast_payment.id,
            'sale_id':self.sale_id.id,
        }

    
    @api.onchange('rate','amount','amount_bs','currency_id')
    def _onchange_rate_amount(self):
        for rec in self:
            if rec.currency_id == self.env.company.currency_id or not rec.currency_id:
                if rec.rate > 0 and rec.amount > 0:
                    rec.amount_bs = rec.amount * rec.rate
            else:
                if rec.rate > 0 and rec.amount_bs > 0:
                    rec.amount = rec.amount_bs / rec.rate

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        for rec in self:
            if rec.sale_id:
                rec.partner_id = rec.sale_id.partner_id.id

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        for rec in self:
            if rec.invoice_id:
                rec.partner_id = rec.partner_id.id
                rec.rate = rec.invoice_id.manual_currency_exchange_rate

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            rec.sale_id = False
            rec.invoice_id = False



