# -*- coding: utf-8 -*-

from odoo import models, fields,api

class ResCompany(models.Model):
    _inherit = "res.company"

    product_nd_id = fields.Many2one("product.product", "Producto para Nota de Débito", tracking=True)
