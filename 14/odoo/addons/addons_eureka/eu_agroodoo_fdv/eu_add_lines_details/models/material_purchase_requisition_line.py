# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderHeridt(models.Model):
    _inherit = 'material.purchase.requisition.line'
    

    categ_id = fields.Many2one(related='product_id.categ_id', store=True , string="Categoria de Producto") 