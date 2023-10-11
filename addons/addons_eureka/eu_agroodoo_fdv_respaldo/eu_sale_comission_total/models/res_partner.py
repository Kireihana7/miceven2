# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    user_comission = fields.Many2one('res.users','Usuario Vinculado')