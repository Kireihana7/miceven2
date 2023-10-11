# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    account_payment_fast = fields.Many2one('account.payment.fast',string="Pago Rápido Vinculado")



