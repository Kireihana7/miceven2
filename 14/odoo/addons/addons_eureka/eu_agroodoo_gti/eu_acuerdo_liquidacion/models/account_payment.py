# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    acuerdo_liquidacion_id = fields.Many2one(
        "acuerdo.liquidacion", 
        "Acuerdo de liquidación",
        tracking=True,
    )
    product_id = fields.Many2one("product.product", "Producto", tracking=True)
    weight = fields.Float("Peso", tracking=True)
    per_weight = fields.Monetary("Precio unitario", tracking=True)
    is_liquidacion = fields.Boolean("Es liquidación", tracking=True)

    @api.onchange("per_weight", "weight")
    def _onchange_weights(self):
        self.update({"amount": self.per_weight * self.weight})