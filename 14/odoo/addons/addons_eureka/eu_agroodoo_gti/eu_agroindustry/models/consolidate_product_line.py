# -*- coding: utf-8 -*-

from odoo import models, fields, _

class ConsolidateProductLine(models.Model):
    _name = "consolidate.product.line"
    _description = "Producto relacionado"

    product_id = fields.Many2one("product.product", "Producto")
    weight = fields.Float("Peso")
    original = fields.Float("Peso estimado")
    consolidate_id = fields.Many2one("chargue.consolidate")