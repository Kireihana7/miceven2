# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    other_company_payment_id = fields.Many2one('account.payment.multi.company',string="Pago Multi Compañía Relacionado",readonly=True)
