# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class QualityCheckTabla(models.Model):
    _name = "quality.check.tabla"
    _description = "Quality Check Tabla"

    quality_check = fields.Many2one('quality.check',string="Orden de Calidad",force_save="1")
    product_id = fields.Many2one(related="quality_check.product_id")
    resultado_esperado = fields.Selection([('conforme','Conforme'),('caracte','Característico'),('no_conforme','No Conforme')],string="Resultado Esperado")
    propiedades = fields.Many2one('product.template.propiedades',string="Propiedades",force_save="1")
    name = fields.Char(related="propiedades.name",string="Nombre")
    operation = fields.Many2one(related="propiedades.operation",string="Operación",force_save="1")
    qty_expected = fields.Float(related="propiedades.qty_expected")
    qty = fields.Float(string="Resultado",force_save="1")
    diferencia = fields.Float(string="Diferencia",compute="_compute_diferencia", store=True)
    resultado = fields.Selection([('conforme','Conforme'),('caracte','Característico'),('no_conforme','No Conforme')],string="Resultado Obtenido")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,tracking=True,invisible=True)
    imprimir = fields.Boolean(string="Imprimir",default=False)
    
    @api.depends('qty','qty_expected')
    def _compute_diferencia(self):
        for rec in self:
            rec.diferencia = rec.qty - rec.qty_expected

    display_type = fields.Selection([
    ('line_section', "Section"),
    ('line_note', "Note")], default=False)
    sequence = fields.Integer(string='Sequence', default=10)