# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPaymentFast(models.Model):
    _inherit = 'account.payment.fast'

    visit_id = fields.Many2one('res.visit',string="Visita relacionada",readonly=True)

class AccountPaymentFastLine(models.Model):
    _inherit = 'account.payment.fast.line'
    
    @api.model
    def default_get(self, fields):
        rec = super(AccountPaymentFastLine, self).default_get(fields)
        context = dict(self._context or {})
        viene_de_visita = context.get('viene_de_visita')
        if viene_de_visita:
            rec.update({
                'partner_id': context.get('partner_id',False),
            })
        return rec