# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # @api.model
    # def create(self, values):
       
    #     line = super(PurchaseOrderLine, self).create(values)
    #     if line.order_id.state == 'purchase':
    #         raise UserError('No puedes añadir una nueva línea')
    #     return line

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # @api.model
    # def create(self, values):
       
    #     line = super(SaleOrderLine, self).create(values)
    #     if line.order_id.state == 'sale':
    #         raise UserError('No puedes añadir una nueva línea')
    #     return line

    # 