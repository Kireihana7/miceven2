# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    vehicle_id = fields.Many2one("fleet.vehicle", "Vehiculo")
    vehicle_service_id = fields.Many2one("fleet.vehicle.log.services", "Servicio")

    @api.constrains("vehicle_id")
    def _check_vehicle_id(self):
        for rec in self.filtered("vehicle_id"):
            if self.search([
                ("id", "!=", rec.id),
                ("vehicle_id", "=", rec.vehicle_id.id),
            ]).filtered(lambda r: not r.stage_id.done):
                raise ValidationError("Ya hay una petición de mantenimiento con este vehículo")

    @api.constrains("vehicle_service_id", "stage_id")
    def _check_service_done(self):
        for rec in self:
            if rec.stage_id.done and rec.vehicle_service_id.state not in ["done", "cancelled"]:
                raise ValidationError("No puedes confirmar el mantenimiento hasta no haber finalizado el servicio")

    @api.onchange("vehicle_id", "equipment_id")
    def _onchange_object(self):
        for rec in self:
            if rec.vehicle_id:
                rec.equipment_id = None

            if rec.equipment_id:
                rec.vehicle_id = None

    #region Actions
    def action_set_vehicle_active(self):
        for rec in self:         
            rec.vehicle_id.active = rec.stage_id.done

    def action_create_service(self):
        self.ensure_one()

        return {
            'type':'ir.actions.act_window',
            'name': "Crear servicio",
            'res_model':'fleet.vehicle.log.services',
            'view_mode':'form',
            "context": {
                "default_maintenance_request_id": self.id,
                "default_vehicle_id": self.vehicle_id.id,
                "default_date_complete": self.request_date,
            },
            'target':'current',
        }
    #endregion

    #region ORM
    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        res.action_set_vehicle_active()

        return res

    def write(self, vals):
        res = super().write(vals)

        self.action_set_vehicle_active()

        return res
    #endregion