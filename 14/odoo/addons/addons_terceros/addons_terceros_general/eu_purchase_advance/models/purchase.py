# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    def show_advance_purchase(self):
        self.ensure_one()
        res = self.env.ref('locv_account_advance_payment.action_account_advance_payment')
        res = res.read()[0]
        res['domain'] = str([('purchase_id', '=', self.id)])
        return res

    advance_count = fields.Integer("Anticipos", compute='_compute_advance_count')

    def _compute_advance_count(self):
        for advance in self:
            advance.advance_count = self.env['account.advanced.payment'].sudo().search_count([('purchase_id', '=', advance.id)])

    advance_id  = fields.One2many("account.advanced.payment","purchase_id",string="Anticipos de Compras")

    monto_advance = fields.Float(string="Monto de los Anticipos", compute="_compute_monto_advance")

    monto_advance_dolar = fields.Float(string="Monto de los Anticipos (Dolar)", compute="_compute_monto_advance")

    currency_id_advance_dolar = fields.Many2one("res.currency", 
        string="Divisa de Referencia",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),invisible=True)

    def _compute_monto_advance(self):
        monto_pago          =   0.0
        monto_pago_dolar    =   0.0
        for rec in self:
            rec.monto_advance         = 0.0
            rec.monto_advance_dolar   = 0.0
            for advance in rec.advance_id:
                if advance.state != 'cancelled':
                    monto_pago          =   advance.currency_id._convert(advance['amount_advance'], rec.currency_id, rec.company_id or self.env.company, advance.date or date.today())
                    monto_pago_dolar    =   advance.currency_id._convert(advance['amount_advance'], rec.currency_id_advance_dolar, rec.company_id or self.env.company, advance.date or date.today())
                    rec.monto_advance +=  monto_pago
                    rec.monto_advance_dolar +=  monto_pago_dolar
