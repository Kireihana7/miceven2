# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('weight')
    def _onchange_weight(self):
        for rec in self:
            rec.product_variant_id.weight = rec.weight

    weight = fields.Float('Weight', digits='Stock Weight',force_save=True)     
    operaciones = fields.One2many('product.template.operation','product_id',string="Operaciones del Producto")
    propiedades = fields.One2many('product.template.propiedades','product_id',string="Propiedades Vinculadas")

    def write(self,vals):
        res = super(ProductTemplate, self).write(vals)
        for rec in self:
            if rec.weight == 0:
                rec.weight = 1
        return res

    @api.model
    def create(self,vals):
        res = super(ProductTemplate, self).create(vals)
        for rec in self:
            if rec.weight == 0:
                rec.weight = 1
        return res

