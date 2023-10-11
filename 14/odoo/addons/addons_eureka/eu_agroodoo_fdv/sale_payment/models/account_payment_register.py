# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    sale_id = fields.Many2one(
        'sale.order',
        string='SO (Venta)',
        copy=False,
    )

    @api.model
    def default_get(self, fields):
        result = super(AccountPaymentRegister, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.move':
            return result
        move_id = self.env['account.move'].browse(self._context.get('active_ids')).filtered(lambda move: move.is_invoice(include_receipts=True))
        result.update({
            'sale_id':move_id[0].sale_id.id,
            })
        return result

    def _create_payment_vals_from_wizard(self):
        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        result.update({
            'sale_id':self.sale_id.id,
        })
        return result