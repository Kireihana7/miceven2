# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"
    
    fuel_log_ids = fields.One2many("fleet.fuel.log", "vehicle_id", "Registro de combustible", tracking=True)
    current_fuel = fields.Float(
        "Combustible actual",
        compute="_compute_current_fuel", 
        tracking=True,
        store=True,
    )
    fuel_rate = fields.Float("Eficiencia de combustible", compute="_compute_fuel_rate", tracking=True,)

    #region Computes
    @api.depends("current_fuel", "odometer")
    def _compute_fuel_rate(self):
        for rec in self:
            rec.fuel_rate = rec.odometer / (rec.current_fuel or 1)

    @api.depends("fuel_log_ids.fuel_quantity", "fuel_log_ids.log_type")
    def _compute_current_fuel(self):
        for rec in self:
            logs = self.fuel_log_ids

            increment = logs \
                .filtered(lambda l: l.log_type == "increment") \
                .mapped("fuel_quantity")

            decrement = logs \
                .filtered(lambda l: l.log_type == "decrement") \
                .mapped("fuel_quantity")

            rec.current_fuel = sum(increment) - sum(decrement)
    #endregion

    @api.constrains("current_fuel")
    def _check_current_fuel(self):
        for rec in self:
            if rec.current_fuel < 0:
                raise ValidationError(_("El nivel de combustible no puede ser menor a cero"))