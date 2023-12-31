# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class AccountPaymentMotivo(models.Model):
    _name = 'account.payment.motivo'
    _description = 'Motivo de Pagos'
    _order = 'id desc'

    name = fields.Char(
        string='Nombre',
        index=True,
    )   
class AccountPayments(models.Model):
    _inherit = 'account.payment'

   
    payment_reg = fields.Date(string='Fecha Efectiva',readonly=True, states={'draft': [('readonly', False)]}, track_visibility='always',default=fields.Date.context_today)
    payment_date_collection = fields.Date(default=fields.Date.context_today, required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False, tracking=True, track_visibility='onchange' )
    gestores = fields.Many2one('res.partner',string="Gestor / Tercero", track_visibility='always',)
    motivo = fields.Many2one('account.payment.motivo', track_visibility='always', string="Motivo de la Transferencia")

    @api.model
    def default_get(self, fields):
        result = super(AccountPayments, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return result
        else:
            move_id = self.env['account.move'].browse(self._context.get('active_ids')).filtered(lambda move: move.is_invoice(include_receipts=True))
            for move in move_id:
                result.update({
                    'date':move.invoice_date,
                    })
            return result

    def _get_invoice_payment_amount(self, inv):
        """
        Computes the amount covered by the current payment in the given invoice.

        :param inv: an invoice object
        :returns: the amount covered by the payment in the invoice
        """
        self.ensure_one()
        return sum([
            data['amount']
            for data in inv._get_reconciled_info_JSON_values()
            if data['account_payment_id'] == self.id
        ])


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

   
    payment_reg = fields.Date(string='Fecha Efectiva',readonly=False,default=fields.Date.context_today)
    payment_date_collection = fields.Date(default=fields.Date.context_today, required=True,  track_visibility='onchange' )
    gestores = fields.Many2one('res.partner',string="Gestor / Tercero", track_visibility='always',)
    motivo = fields.Many2one('account.payment.motivo', track_visibility='always', string="Motivo de la Transferencia")

    def _create_payment_vals_from_wizard(self):
        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        result.update({
            'payment_reg': self.payment_reg,
            'payment_date_collection': self.payment_date_collection,
            'gestores': self.gestores,
            'motivo': self.motivo,
        })
        return result