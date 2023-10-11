# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    zone_id = fields.Many2one("res.partner.zones", "Zona",related="move_id.zone_id",store=True)