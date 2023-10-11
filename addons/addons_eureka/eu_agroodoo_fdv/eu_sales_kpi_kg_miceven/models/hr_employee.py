# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"
    
    zone_id = fields.Many2one("res.partner.zones", "Zona")