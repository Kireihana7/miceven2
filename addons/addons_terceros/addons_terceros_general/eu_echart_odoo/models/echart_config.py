# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError



# class ProductTemplate(models.Model):
#     _inherit = 'product.template'

#     extraccion_blanco = fields.Many2many(
#         'res.company',
#         string='Producto de Extracción Maíz Blanco',
#     )

#     extraccion_amarillo = fields.Many2many(
#         'res.company',
#         string='Producto de Extracción Maíz Amarillo',
#     )

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    extraccion_blanco = fields.Many2many(
        'product.product',
        'extraccion_blanco',
        string='Producto de Extracción Maíz Blanco',
    )

    extraccion_amarillo = fields.Many2many(
        'product.product',
        'extraccion_amarillo',
        string='Producto de Extracción Maíz Amarillo',
    )