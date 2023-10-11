# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    product_payment_id = fields.Many2one('product.product',string="Producto para Factura desde el Pago")
