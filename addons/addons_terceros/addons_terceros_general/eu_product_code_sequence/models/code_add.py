# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def set_default_code_all_products(self):
        for product in self.env["product.product"].search([("default_code", "=", False)]):
            product.default_code = self.env['ir.sequence'].sudo().next_by_code('product.code.seq')

    default_code = fields.Char(readonly=True)
    
    @api.model    
    def create(self, vals):
        res = super().create(vals)

        for rec in res:
            rec.default_code = self.env['ir.sequence'].next_by_code('product.code.seq')
            
        return res