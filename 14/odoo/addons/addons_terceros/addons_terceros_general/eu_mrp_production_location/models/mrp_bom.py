# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round

from itertools import groupby

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    location_dest_id = fields.Many2one('stock.location', 'Destination location')