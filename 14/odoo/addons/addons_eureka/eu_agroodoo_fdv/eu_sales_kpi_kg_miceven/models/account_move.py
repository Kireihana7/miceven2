# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"
    
    zone_id = fields.Many2one("res.partner.zones", "Zona",related="partner_id.zone_id",store=True)