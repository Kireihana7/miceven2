# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import datetime
import math
import operator as py_operator
import re

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import format_date
from odoo.osv import expression

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    # location_dest_id = fields.Many2one('stock.location', 'Destination location', compute='_compute_location_dest_id', store=True)
    
    # @api.depends('bom_id')
    # def _compute_location_dest_id(self):
    #     for rec in self:
    #         rec.location_dest_id = False
    #         if rec.bom_id:
    #             if rec.bom_id.location_dest_id:
    #                 rec.location_dest_id = rec.bom_id.location_dest_id.id

    bom_location_dest_id = fields.Many2one('stock.location', 'Destination location', related='bom_id.location_dest_id', store=False)
    location_dest_id = fields.Many2one('stock.location', 'Destination location')

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        super(MrpProduction, self)._onchange_bom_id()
        # self.location_dest_id = False
        if self.bom_id:
            if self.bom_id.location_dest_id:
                self.location_dest_id = self.bom_id.location_dest_id    

    @api.onchange('location_dest_id', 'move_finished_ids', 'bom_id')
    def _onchange_location_dest(self):
        super(MrpProduction, self)._onchange_location_dest()
        # self.location_dest_id = False
        if self.bom_id:
            if self.bom_id.location_dest_id:
                self.location_dest_id = self.bom_id.location_dest_id           

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        super(MrpProduction, self).onchange_picking_type()
        # self.location_dest_id = False
        if self.bom_id:
            if self.bom_id.location_dest_id:
                self.location_dest_id = self.bom_id.location_dest_id
