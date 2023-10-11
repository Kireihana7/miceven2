# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = "res.partner"

    fleet_trip_ids = fields.One2many("fleet.trip", "driver_id", "Viajes")
    is_traveling = fields.Boolean(compute="_compute_is_traveling", store=True)

    @api.depends("fleet_trip_ids.state")
    def _compute_is_traveling(self):
        for rec in self:
            rec.is_traveling = any(state == "en_proceso" for state in rec.fleet_trip_ids.mapped("state"))