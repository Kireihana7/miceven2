# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MroRequest(models.Model):
    _inherit = "mro.request"

    vehicle_service_id = fields.Many2one(
        "fleet.vehicle.log.services",
        "Servicio",
        tracking=True,
        ondelete="cascade",
    )
    requested_by = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)
    is_closed = fields.Boolean("Está cerrado", compute="_compute_is_closed", tracking=True)

    @api.depends("state")
    def _compute_is_closed(self):
        for rec in self:
            rec.is_closed = rec.state in ["done", "cancel", "reject"]

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res.filtered("vehicle_service_id"):
            rec.vehicle_service_id.mro_request_id = rec.id

        return res

class MroEquipment(models.Model):
    _inherit = "mro.equipment"

    vehicle_id = fields.Many2one("fleet.vehicle", "Vehículo", tracking=True)
    is_vehicle = fields.Boolean("Es un vehículo", tracking=True)

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res.filtered("vehicle_id"):
            rec.vehicle_id.mro_equipment_id = res.id

        return res

class MroMaintenanceTeam(models.Model):
    _inherit = "mro.maintenance.team"

    company_id = fields.Many2one(
        "res.company", 
        "Compañia", 
        default=lambda self: self.env.company,
    )

class MroTool(models.Model):
    _inherit = "mro.tool"

    company_id = fields.Many2one(
        "res.company", 
        "Compañia", 
        default=lambda self: self.env.company,
    )

class MroEquipmentCategory(models.Model):
    _inherit = "mro.equipment.category"

    company_id = fields.Many2one(
        "res.company", 
        "Compañia", 
        default=lambda self: self.env.company,
    )

class MroEquipmentLocation(models.Model):
    _inherit = "mro.equipment.location"

    company_id = fields.Many2one(
        "res.company", 
        "Compañia", 
        default=lambda self: self.env.company,
    )
