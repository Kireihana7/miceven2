# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    monto_total = fields.Float(string="Monto Total Pagado", compute="_compute_monto_total",readonly=True)
    monto_restante  = fields.Float(string="Monto Restante", compute="_compute_monto_total",readonly=True)

    @api.depends('advance_id','payment_id')
    def _compute_monto_total(self):
        monto_total    =   0.0
        for rec in self:
            rec.monto_total    = 0.0
            rec.monto_restante = 0.0
            for advance in rec.advance_id:
                if advance.state != 'cancelled':
                    monto_total     =   advance.currency_id._convert(advance['amount_advance'], rec.currency_id, rec.company_id or self.env.company, advance.date or date.today())
                    rec.monto_total +=  monto_total
            for payment in rec.payment_id:
                if payment.state != 'cancelled':
                    monto_total      =   payment.currency_id._convert(payment['amount'], rec.currency_id, rec.company_id or self.env.company, payment.date or date.today())
                    rec.monto_total  +=  monto_total

            rec.monto_restante = rec.amount_total - rec.monto_total
