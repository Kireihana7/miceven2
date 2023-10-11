# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    vehicle_id = fields.Many2one("fleet.vehicle", "Vehículo")
    vehicle_type_property = fields.Selection(related='vehicle_id.vehicle_type_property')
    license_plate = fields.Char("Licencia", related="vehicle_id.license_plate")
    driver_id = fields.Many2one('res.partner', string="Conductor")

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        if not self.driver_id:
            self.update({"driver_id": self.vehicle_id.driver_id.id})