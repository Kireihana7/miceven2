# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpByProduct(models.Model):
    _inherit = 'mrp.bom.byproduct'

    aprovechable = fields.Boolean(string='Aprovechable', default=False)  