# -*- coding: utf-8 -*-

from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetVehicleDocumentLine(models.Model):
    _name = "fleet.vehicle.document.line"
    _description = "Documentos del vehículo"
    _inherit = "document.mixin"

    def _action_notify_due(self):
        self.env["fleet.vehicle.document.line"] \
            .search([("due_date", "<=", fields.Date.to_string(date.today() - relativedelta(days=5)))]) \
            ._notify_expiration()

    fleet_vehicle_id = fields.Many2one("fleet.vehicle", "Vehículo")
    attachment_id = fields.Many2one("ir.attachment", "Archivo anexado")

    @api.onchange("fleet_vehicle_id")
    def _onchange_fleet_vehicle_id(self):
        if self.fleet_vehicle_id:
            return {
                "domain": {
                    "attachment_id": [("id", "in", self.fleet_vehicle_id.fleet_attach_ids.ids)]
                }
            }

    def _notify_expiration(self):
        for rec in self.sudo():
            rec.activity_schedule(
                "eu_fleet_documents.mail_activity_due_document_fleet_vehicle",
                date.today(),
                summary="Un documento está cerca de vencerse",
                note=f"El documento {rec.name} de el vehículo {rec.fleet_vehicle.name}",
                user_id=rec.vehicle_owner.id,
                request_partner_id=rec.vehicle_owner.partner_id.id,
            )

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    fleet_document_line_ids = fields.One2many(
        "fleet.vehicle.document.line",
        "fleet_vehicle_id", 
        "Documentos"
    )

    @api.constrains("document_ids")
    def _check_document_ids(self):
        for rec in self:
            documents = rec.fleet_document_line_ids

            if len(documents.mapped("document_id.id")) != len(documents):
                raise ValidationError("Los documentos deben ser únicos")