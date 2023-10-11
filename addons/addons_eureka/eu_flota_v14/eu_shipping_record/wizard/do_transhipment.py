# -*- coding: utf-8 -*-

from odoo import models, fields

class DoTranshipment(models.TransientModel):
    _name = "do.transhipment"
    _description = "Transbordo"

    driver_id = fields.Many2one("res.partner", "Conductor")
    vehicle_id = fields.Many2one("fleet.vehicle", "Vehículo")
    fleet_trip_id = fields.Many2one("fleet.trip")
    branch_id = fields.Many2one("res.branch", related="fleet_trip_id.branch_id")
        
    def action_do_transhipment(self):
        self.fleet_trip_id.write({
            "driver_id": self.driver_id.id,
            "vehicle_id": self.vehicle_id.id,
        })