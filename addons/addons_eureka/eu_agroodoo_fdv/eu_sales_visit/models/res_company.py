# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    product_id_visit = fields.Many2many('product.product',string="Productos para Promedio")
