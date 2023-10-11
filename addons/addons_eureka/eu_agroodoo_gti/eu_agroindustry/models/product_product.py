# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    need_romana = fields.Boolean(string="¿Necesita Romana?",default=False)
    auto_validate = fields.Boolean(string="¿Validar Automáticamente?",default=False)
    with_excedente = fields.Boolean(string="¿Registrar Excedente?",default=False)
    product_excedente = fields.Many2one('product.template',string="Producto del Excedente")
    registro_sanitario = fields.Char("Registro sanitario")
    cpe = fields.Char("CPE")
    use_precio_liquidar = fields.Boolean("Usar peso acondicionado")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('need_romana')
    def _onchange_need_romana(self):
        for rec in self:
            if rec.need_romana:
                rec.product_variant_id.need_romana = True

                if rec.weight == 0:
                    rec.product_variant_id.weight = rec.weight = 1
            else:
                rec.product_variant_id.need_romana = False

    need_romana = fields.Boolean(string="¿Necesita Romana?",default=False,onchange=_onchange_need_romana)
    auto_validate = fields.Boolean(string="Validar Automáticamente?",default=False)
    with_excedente = fields.Boolean(string="¿Registrar Excedente?",default=False)
    product_excedente = fields.Many2one('product.template',string="Producto del Excedente")
    registro_sanitario = fields.Char("Registro sanitario")
    cpe = fields.Char("CPE")
    use_precio_liquidar = fields.Boolean("Usar peso acondicionado")

    @api.constrains("weight", "need_romana")
    def _check_weight(self):
        if any(r.need_romana and r.weight == 0 for r in self):
            raise ValidationError("El peso es obligatorio si el producto necesita romana")

    def update_variant(self):
        for rec in self:
            rec.product_variant_id.write({
                "need_romana": rec.need_romana,
                "auto_validate": rec.auto_validate,
                "with_excedente": rec.with_excedente,
                "use_precio_liquidar": rec.use_precio_liquidar,
                "product_excedente": rec.product_excedente.id if rec.product_excedente else None,
            })

    def write(self,vals):
        res = super().write(vals)

        self.update_variant()

        return res

    @api.model
    def create(self,vals):
        res = super().create(vals)
        
        res.update_variant()

        return res

