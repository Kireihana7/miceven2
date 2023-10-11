# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetTripMilestone(models.Model):
    _name = 'fleet.trip.milestone'
    _description = 'Tabulador'
    _inherit = 'fleet.trip.route'

    name = fields.Char("Código", tracking=True)
    currency_id = fields.Many2one(
        "res.currency",
        "Moneda",
        default=lambda self: self.env.company.currency_id, 
        tracking=True,
    )
    note = fields.Char("Nota")
    cost = fields.Monetary("Costo", tracking=True)
    time = fields.Float("Tiempo", tracking=True)
    distance = fields.Float("Distancia (km)", tracking=True)
    can_invoice_trip = fields.Boolean(
        default=lambda self: bool(self.env["ir.config_parameter"].sudo().get_param("eu_shipping_record.can_invoice_trip")),
        store=False,
    )

    @api.onchange("route_type")
    def _onchange_route_type(self):
        for rec in self:
            rec.update({
                "origin_branch_id": None,
                "origin_city_id": None,
                "destination_branch_id": None,
                "destination_city_id": None,
            })
  

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        Sequence = self.env["ir.sequence"]
        CODE = "milestone.sequence"
        COMPANY = self.env.company

        if not Sequence.search([("code", "=", CODE),("company_id", "=", COMPANY.id)]):
            Sequence.create({
                "code": CODE,
                "prefix": "TAB/",
                'name': f"Tabulador en {COMPANY.name}",
                'padding': 6,
                'company_id': COMPANY.id,
            })

        res.write({"name": Sequence.next_by_code(CODE) })

        return res