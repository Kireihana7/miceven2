# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError

class FleetVehicleLogServices(models.Model):
    _inherit = "fleet.vehicle.log.services"

    with_mr = fields.Boolean("Pasar a mantenimiento", tracking=True)
    mro_request_id = fields.Many2one("mro.request", "Petición de mantenimiento", tracking=True)
    mro_order_id = fields.Many2one(
        "mro.order", 
        "Servicio de mantenimiento", 
        tracking=True,
        related="mro_request_id.order_id"
    )
    vehicle_inspection_id = fields.Many2one("fleet.vehicle.inspection", "Inspección", tracking=True)

    def action_create_mro_request(self):
        if not  self.vehicle_id.mro_equipment_id:
            raise UserError("Debes haber creado un equipo con ese vehículo")

        return {
            "name": "Petición de mantenimiento",
            "type": "ir.actions.act_window",
            "res_model": "mro.request",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_equipment_id": self.vehicle_id.mro_equipment_id.id,
                "default_vehicle_service_id": self.id,
                "default_requested_date": fields.Datetime.today(),
                "default_maintenance_priority": "1" if self.priority == "low" \
                    else "2" if self.priority == "normal" \
                    else "3",
            },
        }

    def action_done(self):
        if self.with_mr and not any([self.mro_order_id, self.mro_order_id.state in ["done", "cancel"]]):
            raise UserError("La órden de mantenimiento no está cerrada")

        return super().action_done()

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    mro_equipment_id = fields.Many2one("mro.equipment", "Equipo", tracking=True)

    def action_create_equipment(self):
        return {
            "name": "Equipo",
            "type": "ir.actions.act_window",
            "res_model": "mro.equipment",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_vehicle_id": self.id,
                "default_name": self.name,
                "default_is_vehicle": True,
            },
        }