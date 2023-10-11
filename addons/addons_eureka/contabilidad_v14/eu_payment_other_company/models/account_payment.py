# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    other_company_payment_id_to = fields.Many2one('account.payment.multi.company',string="Pago MultiCompañía Origen",readonly=True)
    other_company_payment_id_from = fields.Many2one('account.payment.multi.company',string="Pago MultiCompañía Destino",readonly=True)

    def unlink(self):
        for rec in self:
            if rec.other_company_payment_id_to or rec.other_company_payment_id_from:
                raise UserError('No puedes borrar un pago que tenga un Traslado vinculado')
        res = super(AccountPayment, self).unlink()

    def action_draft(self):
        for rec in self:
            if rec.state=='cancel' and rec.other_company_payment_id_to:
                raise UserError('No puedes pasar a borrador un pago que tenga un Traslado vinculado')
        res = super(AccountPayment, self).action_draft()
