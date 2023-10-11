# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    

    warehouses_id = fields.Many2one('stock.warehouse', string="Almacén por Defecto")
