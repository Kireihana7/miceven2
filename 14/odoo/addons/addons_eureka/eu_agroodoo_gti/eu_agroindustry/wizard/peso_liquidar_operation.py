# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PesoLiquidarOperation(models.Model):
    _name = "peso.liquidar.operation"
    _description = "Peso por liquidar"

    name = fields.Char("Referencia")
    chargue_consolidate_id = fields.Many2one("chargue.consolidate")
    humedad_liquidar = fields.Float("% de humedad", digits=(20,4))
    impurezas_liquidar = fields.Float("% de impurezas", digits=(20,4))
    peso_liquidar = fields.Float("Peso a liquidar", compute="_compute_peso_liquidar", digits=(20,4))
    peso_neto = fields.Float(related="chargue_consolidate_id.peso_neto")
    peso_neto_trailer = fields.Float(related="chargue_consolidate_id.peso_neto_trailer")
    deduccion_humedad = fields.Float("% Deducción humedad", compute="_compute_deduccion", digits=(20,4))
    deduccion_impurezas = fields.Float("% Deducción impurezas", compute="_compute_deduccion", digits=(20,4))
    peso_deduccion_humedad = fields.Float(
        "Peso deducido por humedad", 
        compute="_compute_peso_deduccion",
        digits=(20,4)
    )
    peso_deduccion_impurezas = fields.Float(
        "Peso deducido por impurezas", 
        compute="_compute_peso_deduccion",
        digits=(20,4)
    )
    peso_full = fields.Float(compute="_compute_peso_full", digits=(20,4), tracking=True)
    currency_id = fields.Many2one(related="chargue_consolidate_id.currency_id")
    location_id = fields.Many2one(related="chargue_consolidate_id.location_dest_id")
    product_price = fields.Monetary(related="chargue_consolidate_id.product_price")
    partner_id = fields.Many2one(related="chargue_consolidate_id.partner_id")
    product_id = fields.Many2one(related="chargue_consolidate_id.product_id")
    chargue_date = fields.Datetime(related="chargue_consolidate_id.date")
    total = fields.Monetary("Total", compute="_compute_total")
    has_peso_liquidar = fields.Boolean(compute="_compute_has_peso_liquidar")

    @api.depends(
        "chargue_consolidate_id.peso_liquidar_operation_ids",
        "chargue_consolidate_id.last_operation_id",
    )
    def _compute_has_peso_liquidar(self):
        for rec in self:
            chargue = rec.chargue_consolidate_id
            rec.has_peso_liquidar = any([
                len(chargue.peso_liquidar_operation_ids) > 1,
                bool(chargue.last_operation_id),
                chargue.last_operation_id != rec.id,
            ])
        

    @api.depends("product_price", "peso_liquidar")
    def _compute_total(self):
        for rec in self:
            rec.total = rec.product_price * rec.peso_liquidar

    @api.depends("peso_neto", "peso_neto_trailer")
    def _compute_peso_full(self):
        for rec in self:
            rec.peso_full = rec.peso_neto + rec.peso_neto_trailer

    @api.depends("deduccion_humedad","deduccion_impurezas","peso_full")
    def _compute_peso_deduccion(self):
        for rec in self:
            rec.peso_deduccion_impurezas = (rec.deduccion_impurezas / 100) * rec.peso_full
            rec.peso_deduccion_humedad = (rec.deduccion_humedad / 100) * (rec.peso_full - rec.peso_deduccion_impurezas)

    @api.depends(
        "chargue_consolidate_id.product_id",
        "humedad_liquidar",
        "impurezas_liquidar"
    )
    def _compute_deduccion(self):
        for rec in self:
            tabla_ids = self.env["tabla.deduccion"].sudo().search([
                ("product_id","=",self.chargue_consolidate_id.product_id.id)
            ])

            rec.deduccion_humedad = sum(tabla_ids \
                .filtered(lambda t: t.table_type == "humedad") \
                .line_ids \
                .filtered(lambda l: round(l.value, 4) == rec.humedad_liquidar) \
                .mapped("deduccion")
            )

            rec.deduccion_impurezas = sum(tabla_ids \
                .filtered(lambda t: t.table_type == "impureza") \
                .line_ids \
                .filtered(lambda l: round(l.value, 4) == rec.impurezas_liquidar) \
                .mapped("deduccion")
            )
            
    @api.onchange("chargue_consolidate_id","humedad_consolidate","impurezas_consolidate")
    def _onchange_chargue_consolidate_id(self):
        consolidate = self.chargue_consolidate_id

        self.update({
            "humedad_liquidar": consolidate.humedad,
            "impurezas_liquidar": consolidate.impureza,
        })

    @api.depends("peso_full", "peso_deduccion_humedad", "peso_deduccion_impurezas")
    def _compute_peso_liquidar(self):
        for rec in self:
            rec.peso_liquidar = rec.peso_full - rec.peso_deduccion_impurezas - rec.peso_deduccion_humedad

    def action_save(self):
        return {}

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res:
            rec.name = self.env["ir.sequence"].next_by_code("liquidar.operation.seq")

        return res