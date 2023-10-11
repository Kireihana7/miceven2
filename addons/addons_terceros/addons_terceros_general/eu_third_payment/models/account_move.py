# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    third_payment = fields.Boolean(string="Pagar a Tercero")
    autorizado = fields.Many2one('res.partner.autorizados',domain="[('partner_id','=',partner_id)]")

    