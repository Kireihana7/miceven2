# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    user_ids = fields.Many2one(string='Comercial', related='move_id.user_id', store=True)

    move_type    = fields.Selection(related='move_id.move_type', store=True)

    categ_id = fields.Many2one(related='product_id.categ_id',store=True , string="Categoria de Producto") 