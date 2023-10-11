# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrmTeam(models.Model):
    _inherit = "crm.team"
    
    zone_id = fields.Many2one("res.partner.zones", "Zona")