# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    zone_id = fields.Many2one("res.partner.zones", "Zona",tracking=True)
    
    def _synchronize_to_moves(self, changed_fields):
        super()._synchronize_to_moves(changed_fields)

        self.move_id.zone_id = self.zone_id.id

    @api.onchange('partner_id')
    def _onchange_partner_kpi(self):
        for rec in self:
            rec.zone_id = rec.partner_id.user_id.id

class AccountPaymentRegisters(models.TransientModel):
    _inherit = 'account.payment.register'

    zone_id = fields.Many2one("res.partner.zones", "Zona",tracking=True)

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

        result.update({'zone_id': move_id[0].zone_id.id or False})

        return result

    def _create_payment_vals_from_wizard(self):
        result = super()._create_payment_vals_from_wizard()

        result.update({'zone_id': self.zone_id.id})

        return result