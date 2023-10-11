# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    invoice_user_id =fields.Many2one('res.users', string="Comercial", tracking=True)

    def _synchronize_to_moves(self, changed_fields):
        super()._synchronize_to_moves(changed_fields)

        self.move_id.invoice_user_id = self.invoice_user_id.id

    @api.onchange('partner_id')
    def _onchange_partner_kpi(self):
        for rec in self:
            rec.invoice_user_id = rec.partner_id.user_id.id

class AccountPaymentRegisters(models.TransientModel):
    _inherit = 'account.payment.register'

    invoice_user_id = fields.Many2one('res.users',string="Comercial",tracking=True)

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)

        CONTEXT: dict = self._context

        active_ids = CONTEXT.get('active_ids', CONTEXT.get('active_id'))
        active_model: str = CONTEXT.get('active_model')

        if not active_ids or (active_model != 'account.move'):
            return result

        move_id = self.env['account.move'] \
            .browse(active_ids) \
            .filtered(lambda move: move.is_invoice(include_receipts=True))

        result.update({'invoice_user_id': move_id[0].invoice_user_id.id or False})

        return result

    def _create_payment_vals_from_wizard(self):
        result = super()._create_payment_vals_from_wizard()

        result.update({'invoice_user_id': self.invoice_user_id.id})

        return result