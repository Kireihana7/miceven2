# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SeedVariety(models.Model):
    _inherit = 'seed.variety'

    crop_id = fields.Many2one(
        'farmer.location.crops',
        string="Crop",
        required=True,
        tracking=True
    )       

