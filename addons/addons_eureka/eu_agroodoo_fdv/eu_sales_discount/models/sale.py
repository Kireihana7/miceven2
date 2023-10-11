# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _,exceptions
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sale order discount"

    discount_total  = fields.Monetary(string="Total Descuento", compute="_compute_discount", store=True,)

    @api.depends('order_line.discount')
    def _compute_discount(self):

        for order in self:
            discount_total = 0.0
            for line in order.order_line:
                sub = line.price_unit * line.product_uom_qty
                tot = (sub * line.discount) / 100
                discount_total += tot
            order.update({
                'discount_total': discount_total,
            })


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _description = "Sale order discount"
    
    
    







    