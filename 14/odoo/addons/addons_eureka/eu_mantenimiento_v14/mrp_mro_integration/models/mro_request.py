# -*- coding: utf-8 -*-

from odoo import api, fields, models, _



class MroRequest(models.Model):
    _inherit = 'mro.request'


    production_id = fields.Many2one('mrp.production', 'Production Order', readonly=True)
