# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class GuideConsolidateProduct(models.Model):
    _name = 'guide.consolidate.product'
    _description ="Picking Guide Products"

    name = fields.Char(string="Nombre del Producto")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always',invisible=True)
    guide_consolidate_id_product = fields.Many2one(
        comodel_name='guide.consolidate',
        string='Picking Guide', 
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        readonly=True,
        store=True,
    )
    quantity_done = fields.Float(
        string="Quantity Done",
        readonly=True,
        store=True,
    )
    weight = fields.Float(
        string="Weight",
        store=True,
    )
    volume = fields.Float(
        string="Volume", 
        store=True
    )