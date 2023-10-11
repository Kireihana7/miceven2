# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    nro_part = fields.Char(string="Código ERP")
    product_brand_id = fields.Many2one('pos.product.brand', 'Marca')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    nro_part = fields.Char(string="Código ERP",)
    product_brand_id = fields.Many2one(related="product_tmpl_id.product_brand_id")

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    nro_part=fields.Char(related='product_id.nro_part')

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    nro_part=fields.Char(related='product_id.nro_part')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    nro_part=fields.Char(related='product_id.nro_part')
