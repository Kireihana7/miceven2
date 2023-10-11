# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    maintenance_request_id = fields.Many2one("maintenance.request", "Petición de mantenimiento")

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    maintenance_request_id = fields.Many2one("maintenance.request", "Petición de mantenimiento")

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res:
            res.maintenance_request_id.vehicle_service_id = rec.id

        return res