# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit='product.template'

    history_auxiliar = fields.Boolean(compute="_compute_history_auxiliar", store=True)
    history_price_ids = fields.One2many('product.price.history', 'product_tmpl_id')

    @api.depends("standard_price")
    def _compute_history_auxiliar(self):        
        for rec in self:
            history_vals = {
                "name": rec.name,
                "currency_id": rec.currency_id.id,
                "cost": rec.standard_price,
                "company_id": (rec.company_id or self.env.company).id,
                "product_category_id": rec.categ_id.id,
            }

            if self._name == "product.product":
                history_vals.update({
                    "product_id": rec.id,
                    "product_tmpl_id": rec.product_tmpl_id.id,
                })
            else:
                history_vals["product_tmpl_id"] = rec.id

            self.history_price_ids.create(history_vals)
            rec.history_auxiliar = 1

class ProductProduct(models.Model):
    _inherit='product.product'
    
    history_price_ids = fields.One2many('product.price.history', 'product_id')