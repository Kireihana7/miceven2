# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_source_warehouse_id = fields.Many2one('purchase.source.warehouse', string="Almacén Origen", tracking=True)






    