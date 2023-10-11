# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    liquidacion_id = fields.Many2one("acuerdo.liquidacion", "Liquidación",)

class ChargueConsolidate(models.Model):
    _inherit = "chargue.consolidate"

    liquidacion_id = fields.Many2one("acuerdo.liquidacion", "Liquidación",)
    has_liquidacion = fields.Boolean(compute="_compute_has_liquidacion", tracking=True,)

    @api.depends('partner_id')
    def _compute_has_liquidacion(self):
        for rec in self:
            rec.has_liquidacion = bool(self.env["acuerdo.liquidacion"].search([
                ('partner_id','=',rec.partner_id.id),
                ('state', '=', 'anticipo')
            ], limit=1))

    def action_create_po(self):
        res = super().action_create_po()

        for rec in self:
            rec.purchase_id.liquidacion_id = rec.liquidacion_id

        return res 