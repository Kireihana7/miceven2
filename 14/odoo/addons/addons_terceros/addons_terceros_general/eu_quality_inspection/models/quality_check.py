# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError

class QualityCheck(models.Model):
    _inherit = "quality.check"

    @api.model
    def _default_tolerancia_id(self):
        return self.env['quality.tolerancia'].search([
            ('company_id', '=', self.env.company.id),
            ('product_id', '=', self.product_id.id)
        ],limit=1)

    with_obs = fields.Boolean(string="Aprobado con Observación",defalt=False)
    product_tmpl_id = fields.Many2one('product.template',string="Producto Plantilla",related="product_id.product_tmpl_id")
    quality_motivo = fields.One2many('quality.check.motivo','quality_check',string="No Conformidades")
    approve_with_obs = fields.Boolean('Aprobado bajo Observación',default=False)

    # Campos Tolerancia
    tolerancia_id = fields.Many2one('quality.tolerancia',string="Tabla de Tolerancia",default=_default_tolerancia_id)
    line_ids = fields.One2many("quality.check.line", "quality_check_id", "Checks")
    product_operation = fields.Many2one('product.template.operation',string="Operación",domain="[('product_id','=',product_tmpl_id)]")
    quality_tabla = fields.One2many('quality.check.tabla','quality_check',string="Tabla de Propiedades",)
    product_id_variant = fields.Many2one(related="product_id.product_variant_id",)

    @api.onchange("tolerancia_id")
    def _onchange_tolerancia_id(self):
        for rec in self:
            if rec.tolerancia_id.line_ids:
                rec.line_ids = [(5, 0, 0)]
                rec.line_ids = [(0, 0, {"tolerancia_line_id": line.id}) for line in rec.tolerancia_id.line_ids]
            else:
                rec.line_ids = None

    # Vaciar Operaciones
    @api.onchange('product_id')
    def onchange_product_id(self):
        line_dict = {}
        for rec in self:
            if rec.quality_tabla:
                for lines in rec.quality_tabla:
                    values = [(5, 0, 0)]
                    rec.update({'quality_tabla': values})
            if rec.product_operation:
                rec.product_operation = False
     # Traer Operaciones
    @api.onchange('product_operation')
    def onchange_operation(self):
        line_dict = {}
        for rec in self:
            if rec.product_id:
                if rec.quality_tabla:
                    for lines in rec.quality_tabla:
                        values = [(5, 0, 0)]
                        rec.update({'quality_tabla': values})
                orders = [line for line in sorted(rec.env['product.template.propiedades'].search([('product_id', '=', rec.product_id.product_tmpl_id.id),('operation','=',rec.product_operation.id)]),
                    key=lambda x: x.sequence)]
                for order in orders:
                    line_dict = {
                        'product_id':  order.product_id.id,
                        'propiedades':  order.id,
                        'resultado_esperado': order.resultado,
                        'qty_expected': order.qty_expected,
                        'qty': 0.0,
                        'sequence': order.sequence,
                        'display_type': order.display_type,
                        'name': order.name,
                    }
                    lines = [(0,0,line_dict)]
                    rec.write({'quality_tabla':lines})

class QualityCheckLine(models.Model):
    _name = "quality.check.line"
    _description = "Quality check line"

    tolerancia_line_id = fields.Many2one("quality.tolerancia.line", "Nombre", ondelete="cascade")
    name = fields.Char(related="tolerancia_line_id.name")
    quality_check_id = fields.Many2one("quality.check", "Quality check")
    value = fields.Char("Valor obtenido")
    original_value = fields.Char("Valor de referencia", related="tolerancia_line_id.value")
    diff = fields.Char("Diferencia", compute="_compute_diff")

    @api.depends("original_value", "value", "tolerancia_line_id.value_type")
    def _compute_diff(self):
        for rec in self:
            try:
                float(rec.value.replace(",", "."))
                is_float = True
            except:
                is_float = False

            if not all([rec.value, rec.original_value]):
                rec.diff = None
                continue

            if rec.tolerancia_line_id.value_type == "text" or not is_float:
                rec.diff = None
            else:
                rec.diff = "{:.4f}".format(float(rec.value.replace(",", ".")) - float(rec.original_value.replace(",", ".")))