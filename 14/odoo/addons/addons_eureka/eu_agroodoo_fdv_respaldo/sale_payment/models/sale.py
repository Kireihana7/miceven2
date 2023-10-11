# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def show_payment_sale(self):
        self.ensure_one()
        res = self.env.ref('account.action_account_payments')
        res = res.read()[0]
        res['domain'] = str([('sale_id', '=', self.id)])
        return res

    payment_count = fields.Integer("Pago", compute='_compute_payment_count')

    @api.depends('company_id')
    def _compute_payment_count(self):
        for payment in self:
            payment.payment_count = self.env['account.payment'].sudo().search_count([('sale_id', '=', payment.id),('company_id', '=', payment.company_id.id)])
    
    payment_id  = fields.One2many("account.payment","sale_id",string="Pagos de Ventas")

    monto_anticipos = fields.Float(string="Monto de los Pagos", compute="_compute_monto_anticipos")

    monto_anticipos_dolar = fields.Float(string="Monto de los Pagos (Ref)", compute="_compute_monto_anticipos")

    currency_id_payment_dolar = fields.Many2one("res.currency", 
        string="Divisa de Referencia",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),invisible=True)

    def _compute_monto_anticipos(self):
        monto_pago          =   0.0
        monto_pago_dolar    =   0.0
        for rec in self:
            rec.monto_anticipos         = 0.0
            rec.monto_anticipos_dolar   = 0.0
            if self.user_has_groups('account.group_account_readonly') or self.user_has_groups('account.group_account_invoice') or self.user_has_groups('account.group_account_user') or self.user_has_groups('account.group_account_manager') :
                for payment in rec.payment_id:
                    if payment.state != 'cancelled':
                        if rec.currency_id == self.env.company.currency_id:
                            monto_pago  =   payment.amount if payment.currency_id == rec.currency_id else payment.amount_ref
                            monto_pago_dolar  =   payment.amount if payment.currency_id != rec.currency_id else payment.amount_ref
                        else:
                            monto_pago  =   payment.amount if payment.currency_id != rec.currency_id else payment.amount_ref
                            monto_pago_dolar  =   payment.amount if payment.currency_id == rec.currency_id else payment.amount_ref
                        rec.monto_anticipos +=  monto_pago
                        rec.monto_anticipos_dolar +=  monto_pago_dolar

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({
            'sale_id': self.id,
            })
        return result