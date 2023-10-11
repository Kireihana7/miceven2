# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    company_ids = fields.Many2many('res.company',string="Compañías Múltiples",)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    company_ids = fields.Many2many('res.company',string="Compañías Múltiples",related="product_tmpl_id.company_ids")