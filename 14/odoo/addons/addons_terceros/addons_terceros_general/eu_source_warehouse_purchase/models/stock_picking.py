# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    purchase_source_warehouse_id = fields.Many2one('purchase.source.warehouse', related="chargue_consolidate_create.purchase_source_warehouse_id", string="Almacén Origen", store=True, tracking=True)