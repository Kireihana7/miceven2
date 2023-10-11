# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class ProductTemplateOperation(models.Model):
    _name = "product.template.operation"
    _description = "Product Template Operation"

    name = fields.Char(string="Nombre")
    product_id = fields.Many2one('product.template',string="Producto")
    propiedades = fields.One2many('product.template.propiedades','operation',string="Propiedades")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,tracking=True,invisible=True)
    