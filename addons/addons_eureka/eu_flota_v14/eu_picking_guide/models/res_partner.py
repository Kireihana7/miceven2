# -*- coding: utf-8 -*-

from odoo import _, api, fields, models 

class ResPartner(models.Model):
    _inherit = "res.partner"

    zone = fields.Many2one("partner.zone", string="Zone")
    