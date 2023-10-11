    # -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TablaDeduccion(models.Model):
    _name = 'tabla.deduccion'
    _description = "Deducciones automáticas"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre", compute="_compute_name", tracking=True)
    product_id = fields.Many2one("product.product", "Producto", tracking=True)
    table_type = fields.Selection([("humedad", "Humedad"),("impureza","Impureza")], "Tipo de tabla", default="humedad")
    line_ids = fields.One2many("tabla.deduccion.line", "parent_id", "Deducciones", tracking=True)

    @api.depends("product_id.name")
    def _compute_name(self):
        for rec in self:
            rec.name = "Tabla de deducción para " + rec.product_id.name if rec.product_id else ""
            
    @api.depends("product_id")
    def _check_product_id(self):
        for rec in self:
            if self.search([
                ("id","!=",rec.id),
                ("product_id","=",rec.product_id.id),
                ("table_type","=",rec.table_type),
            ], limit=1):
                raise ValidationError("No puedes crear más de una tabla por producto")

class TablaDeduccionLine(models.Model):
    _name = 'tabla.deduccion.line'
    _description = "Deducciones automáticas"

    parent_id = fields.Many2one("tabla.deduccion", ondelete="cascade")
    value = fields.Float(digits=(20,4))
    deduccion = fields.Float(digits=(20,4))

    def write(self, vals):
        for rec in self:
            if "value" in vals:
                rec.parent_id.message_post(body="Se ha cambiado el valor de {} a {}".format(rec.value, vals["value"]))

            if "deduccion" in vals:
                rec.parent_id.message_post(body="Se ha cambiado el valor de {} a {}".format(rec.deduccion, vals["deduccion"]))

        return super().write(vals)