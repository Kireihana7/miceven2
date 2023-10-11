# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    fleet_trip_ids = fields.One2many("fleet.trip", "vehicle_id", "Viajes", tracking=True,)
    weight_limit = fields.Float("Capacidad de carga", tracking=True)
    branch_id = fields.Many2one("res.branch", "Sucursal", tracking=True)
    is_traveling = fields.Boolean(
        "En viaje", 
        compute="_compute_is_traveling", 
        store=True, 
        tracking=True,
    )

    @api.depends("fleet_trip_ids.state")
    def _compute_is_traveling(self):
        for rec in self:
            rec.is_traveling = any(trip.state == "en_proceso" for trip in rec.fleet_trip_ids)
    
class FleetVehicleOdometer(models.Model):
    _inherit = "fleet.vehicle.odometer"

    fleet_trip_id = fields.Many2one("fleet.trip", "Viaje asociado", tracking=True)

class FleetFuelLog(models.Model):
    _inherit = "fleet.fuel.log"

    fleet_trip_id = fields.Many2one("fleet.trip", "Viaje asociado", tracking=True)