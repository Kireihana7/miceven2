# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    def show_payment_purchase(self):
        self.ensure_one()
        res = self.env.ref('account.action_account_payments_payable')
        res = res.read()[0]
        res['domain'] = str([('purchase_id', '=', self.id)])
        return res

    payment_count = fields.Integer("Pagos", compute='_compute_payment_count')

    def _compute_payment_count(self):
        for payment in self:
            payment.payment_count = self.env['account.payment'].search_count([('purchase_id', '=', payment.id)])

    payment_id  = fields.One2many("account.payment","purchase_id",string="Pagos de Compras")

    monto_anticipos = fields.Float(string="Monto de los Pagos", compute="_compute_monto_anticipos")

    monto_anticipos_dolar = fields.Float(string="Monto de los Pagos (Dolar)", compute="_compute_monto_anticipos")

    currency_id_payment_dolar = fields.Many2one("res.currency", 
        string="Divisa de Referencia",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),invisible=True)

    def _compute_monto_anticipos(self):
        monto_pago          =   0.0
        monto_pago_dolar    =   0.0
        for rec in self:
            rec.monto_anticipos         = 0.0
            rec.monto_anticipos_dolar   = 0.0
            for payment in rec.payment_id:
                if payment.state != 'cancelled':
                    monto_pago          =   payment.currency_id._convert(payment['amount'], rec.currency_id, rec.company_id or self.env.company, payment.date or date.today())
                    monto_pago_dolar    =   payment.currency_id._convert(payment['amount'], rec.currency_id_payment_dolar, rec.company_id or self.env.company, payment.date or date.today())
                    rec.monto_anticipos +=  monto_pago
                    rec.monto_anticipos_dolar +=  monto_pago_dolar
