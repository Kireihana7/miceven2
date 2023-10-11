# -*- coding: utf-8 -*-
from odoo import api, fields, models, _ 

class AccountPayment(models.Model):
    _inherit='account.payment'

    iae_entry = fields.Many2one('account.move',string="Pago de IAE Relacionado")
    iae_entry_amount = fields.Monetary(string="Monto del Pago de IAE Relacionado", related="iae_entry.amount_total")
