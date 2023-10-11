# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _,exceptions
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Account invoice discount"

    discount_total  = fields.Monetary(string="Total Descuento", compute="_compute_discount")

    @api.depends('invoice_line_ids.discount')
    def _compute_discount(self):
        for order in self:
            discount_total = 0.0
            for line in order.invoice_line_ids:
                sub = line.price_unit * line.quantity
                tot = sub * (line.discount / 100)
                discount_total += tot
            order.discount_total = discount_total


            

    
    
    







    