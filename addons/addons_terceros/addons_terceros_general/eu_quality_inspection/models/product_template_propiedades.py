# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class ProductTemplatePropiedades(models.Model):
    _name = "product.template.propiedades"
    _description = "Product Template Propiedades"

    name = fields.Char(string="Nombre")
    operation = fields.Many2one('product.template.operation',string="Operaciones")
    product_id = fields.Many2one(related="operation.product_id",string="Producto",store=True)
    qty_expected = fields.Float(string="Cantidad Esperada",default=0)
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,tracking=True,invisible=True)
    display_type = fields.Selection([
    ('line_section', "Section"),
    ('line_note', "Note")], default=False)
    sequence = fields.Integer(string='Sequence', default=10)
    resultado = fields.Selection([('conforme','Conforme'),('caracte','Característico'),('no_conforme','No Conforme')],string="Resultado")