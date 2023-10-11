# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    large_description = fields.Char(string="Descripción Larga")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    large_description = fields.Char(string="Descripción Larga",related="product_tmpl_id.large_description")


    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        res = super(ProductProduct,self).get_product_multiline_description_sale()
        name = self.display_name
        if self.description_sale:
            name += '\n' + self.description_sale 
        if self.large_description:
        	name += '\n' + self.large_description
        return name

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _get_product_purchase_description(self, product_lang):
        res = super(PurchaseOrderLine,self)._get_product_purchase_description(product_lang)
        self.ensure_one()
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase
        if product_lang.large_description:
            name += '\n' + product_lang.large_description
        return name