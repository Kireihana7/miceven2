# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductPriceHistory(models.Model):
    _name = 'product.price.history'
    _description='Historial de costo de productos'
    
    product_id = fields.Many2one("product.product", "Producto")
    product_tmpl_id = fields.Many2one("product.template", "Template")
    name = fields.Char("Nombre")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    origin = fields.Char("Origen")
    cost = fields.Monetary("Costo")
    company_id = fields.Many2one("res.company", "Compañia", default=lambda self: self.env.company)
    product_category_id = fields.Many2one("product.category", "Categoria de producto")