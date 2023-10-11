# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class QualityCheckTabla(models.Model):
    _inherit = "quality.check.tabla"

    product_id = fields.Many2one(related="quality_check.product_id", store=True)
    name = fields.Char(related="propiedades.name",string="Nombre", store=True)
    operation = fields.Many2one(related="propiedades.operation",string="Operación",force_save="1",store=True)
    qty_expected = fields.Float(related="propiedades.qty_expected",store=True)