# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class QualityTolerancia(models.Model):
    _name = 'quality.tolerancia'
    _description ="Tolerancia de Calidad"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,invisible=True,tracking=True)
    name = fields.Char(string="Nombre")
    product_id = fields.Many2one('product.product',string="Producto Relacionado")
    line_ids = fields.One2many("quality.tolerancia.line", "parent_id", "Lineas", tracking=True)

    @api.model    
    def create(self, vals):       
        res = super().create(vals)

        res.write({'name': self.env['ir.sequence'].next_by_code('quality.tolerancia.seq')})

        return res

    @api.constrains("line_ids")
    def _check_line_ids(self):
        for rec in self:
            if len(rec.line_ids.filtered(lambda l: l.is_humedad)) > 1:
                raise ValidationError("No puedes tener más de una humedad")
            elif len(rec.line_ids.filtered(lambda l: l.is_impureza)) > 1:
                raise ValidationError("No puedes tener más de una impureza")

class TablaCalidadLine(models.Model):
    _name = 'quality.tolerancia.line'
    _description = "Linea de Tabla de calidad"

    name = fields.Char("Criterio")
    value = fields.Char("Valor")
    parent_id = fields.Many2one("quality.tolerancia")
    value_type = fields.Selection([
        ("numeric", "Número"),
        ("text","Texto"),
        ("percentage", "Porcentaje"),
    ], "Tipo de valor", default="text")
    is_required = fields.Boolean("Es requerida")
    is_humedad = fields.Boolean("Es humedad")
    is_impureza = fields.Boolean("Es impureza")

    @api.constrains("value", "value_type")
    def _check_value(self):
        try:
            (rec.get_value for rec in self)
        except Exception as e:
            raise ValidationError(e)

    @property
    def get_value(self):
        self.ensure_one()

        return str(self.value) if self.value_type == "text" else float(self.value)