# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    monto_total = fields.Float(string="Monto Total Pagado", compute="_compute_monto_total",readonly=True)
    monto_restante  = fields.Float(string="Monto Restante", compute="_compute_monto_total",readonly=True)

    @api.depends('payment_id','amount_total')
    def _compute_monto_total(self):
        monto_total    =   0.0
        for rec in self:
            rec.monto_total    = 0.0
            rec.monto_restante = 0.0
            for payment in rec.payment_id:
                if payment.state != 'cancelled':
                    if rec.currency_id == self.env.company.currency_id:
                        monto_total  =   payment.amount if payment.currency_id == rec.currency_id else payment.amount_ref
                    else:
                        monto_total  =   payment.amount if payment.currency_id == rec.currency_id else payment.amount_ref
                    rec.monto_total  +=  monto_total

            rec.monto_restante = rec.amount_total - rec.monto_total

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        if 'monto_total' not in fields or 'monto_restante' not in fields:
            return super(PurchaseOrder, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(PurchaseOrder, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['monto_total'] = sum(quant.monto_total for quant in quants)
                group['monto_restante'] = sum(quant.monto_restante for quant in quants)
        return res