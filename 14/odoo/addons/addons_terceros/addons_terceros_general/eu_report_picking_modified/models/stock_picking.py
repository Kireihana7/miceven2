# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, modules,fields
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit="stock.picking"


    check_conformity=fields.Boolean("¿Esta conforme?",tracking=True)