# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    

    categ_id = fields.Many2one(related='product_id.categ_id',store=True , string="Categoria de Producto") 