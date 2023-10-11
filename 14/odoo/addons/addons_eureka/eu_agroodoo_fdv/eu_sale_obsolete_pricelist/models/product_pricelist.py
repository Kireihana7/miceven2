# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    obsolete_rate = fields.Boolean('Tarifa Obsoleta')
    
    