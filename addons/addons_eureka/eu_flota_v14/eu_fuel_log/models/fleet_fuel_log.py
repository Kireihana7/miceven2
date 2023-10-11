# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FleetFuelLog(models.Model):
    _name = 'fleet.fuel.log'
    _description = "Fleet fuel log"

    # Vehicle related fields
    vehicle_id = fields.Many2one("fleet.vehicle", "Vehículo", tracking=True,)
    name = fields.Char("Registro", tracking=True,)
    driver_id = fields.Many2one("res.partner", "Conductor", related="vehicle_id.driver_id", tracking=True,)
    fuel_type = fields.Selection("Tipo de combustible", related="vehicle_id.fuel_type", tracking=True,)
    odometer_unit = fields.Selection("Unidad del odómetro", related="vehicle_id.odometer_unit", tracking=True,)
    current_odometer_value = fields.Float(
        "Odómetro actual", 
        related="vehicle_id.odometer",
        tracking=True,
        store=True,
    )
    new_odometer_value = fields.Float("Nuevo odómetro", tracking=True)
    current_fuel = fields.Float(
        "Combustible actual",
        related="vehicle_id.current_fuel",
        store=True,
        tracking=True,
    )

    # Fuel service
    fuel_quantity = fields.Float("Litros", tracking=True,)
    filling_date = fields.Datetime("Fecha de servicio", tracking=True,)
    log_type = fields.Selection([
        ("increment", "Increment"),
        ("decrement", "Decrement")
    ], "Tipo de registro", default="increment", tracking=True)

    # Costs
    currency_id = fields.Many2one(
        "res.currency",
        "Moneda",
        default=lambda self: self.env.company.currency_id,
        tracking=True,
    )
    price_per_unit = fields.Monetary("Precio por litro", tracking=True,)
    total = fields.Monetary("Total", compute="_compute_total", tracking=True,)

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        Sequence = self.env['ir.sequence']
        COMPANY = self.env.company
        CODE = "fuel.log.sequence"

        if not Sequence.search([("code", "=", CODE),("company_id", "=", COMPANY.id)]):
            Sequence.create({
                "code": CODE,
                "prefix": "FUEL/",
                'name': f"Fuel log for {COMPANY.name}",
                'padding': 6,
                'company_id': COMPANY.id,
            })

        res.write({"name": Sequence.next_by_code(CODE),})

        for rec in res:
            self.env["fleet.vehicle.odometer"].create({
                "value": rec.new_odometer_value,
                "vehicle_id": rec.vehicle_id.id,
                "date": rec.filling_date or fields.Date.context_today(rec),
                "driver_id": self.driver_id.id,
            })

        return res

    #region Constrains
    @api.constrains("new_odometer_value")
    def _check_new_odometer_value(self):
        for rec in self:
            if rec.new_odometer_value <= 0:
                raise ValidationError(_("El valor del odómetro es obligatorio"))

    @api.constrains("total")
    def _check_total(self):
        for rec in self:
            if rec.total < 0:
                raise ValidationError(_("El total no puede ser menor a cero"))
    #endregion

    @api.depends("price_per_unit", "fuel_quantity")
    def _compute_total(self):
        for rec in self:
            rec.total = rec.price_per_unit * rec.fuel_quantity