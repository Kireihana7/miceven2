# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetTripProduct(models.Model):
    _name = "fleet.trip.product"
    _description = "Productos de viajes"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre", tracking=True,)

class FleetTripReturnLine(models.Model):
    _name = 'fleet.trip.return.line'
    _description = 'Devolución de viajes'

    line_id = fields.Many2one('fleet.trip.line', "Producto", ondelete="cascade")
    name = fields.Char("Linea", related="line_id.name")
    weight = fields.Float("Peso", related="line_id.weight")
    fleet_trip_id = fields.Many2one('fleet.trip', "Viaje", ondelete="cascade")

    quantity = fields.Float("Cantidad devuelta")
    reason = fields.Text("Razón")
    total_measure = fields.Float("Total Kg", compute="_compute_total_measure")
    
    @api.depends("quantity", "weight")
    def _compute_total_measure(self):
        for rec in self:
            rec.total_measure = rec.quantity * rec.weight

    @api.onchange("fleet_trip_id")
    def _onchange_fleet_trip_id(self):
        if self.fleet_trip_id:
            return {
                "domain": {
                    "line_id": [("id", "in", self.fleet_trip_id.line_ids.ids)]
                }
            }
  
class FleetTripLine(models.Model):
    _name = 'fleet.trip.line'
    _description = 'Productos de viajes'

    product_id = fields.Many2one("fleet.trip.product", "Producto", ondelete="cascade")
    fleet_trip_id = fields.Many2one('fleet.trip', "Viaje", ondelete="cascade")
    quantity = fields.Float("Cantidad")
    returned_weight = fields.Float("Devuelto Kg", compute="_compute_returned_weight")
    delivered_weight = fields.Float("Despachado Kg", compute="_compute_delivered_weight")
    total_measure = fields.Float("Total Kg", compute="_compute_total_measure")
    to_ship_weight = fields.Float("Cantidad a entregar Kg", compute="_compute_to_ship_weight")

    # Related from product_id
    weight = fields.Float("Peso Kg")
    name = fields.Char("Nombre", related="product_id.name")
    returned_line_ids = fields.One2many("fleet.trip.return.line", "line_id", "Línea devuelta")

    #region Computes
    @api.depends("total_measure", "delivered_weight", "returned_weight")
    def _compute_to_ship_weight(self):
        for rec in self:
            rec.to_ship_weight = rec.total_measure - rec.delivered_weight - rec.returned_weight

    @api.depends("returned_weight", "total_measure")
    def _compute_delivered_weight(self):
        for rec in self:
            if rec.fleet_trip_id.state not in ["planificado", "en_proceso"]:
                rec.delivered_weight = rec.total_measure - rec.returned_weight
            else:
                rec.delivered_weight = 0
            
    @api.depends("quantity", "weight")
    def _compute_total_measure(self):
        for rec in self:
            rec.total_measure = rec.quantity * rec.weight

    @api.depends("returned_line_ids.total_measure")
    def _compute_returned_weight(self):
        for rec in self:
            rec.returned_weight = sum(rec.returned_line_ids.mapped("total_measure"))
    #endregion

    #region Constrains
    @api.constrains("weight")
    def _check_weight(self):
        for rec in self:
            if rec.weight <= 0:
                raise ValidationError("El peso no puede ser cero")

    @api.constrains("total_measure", "returned_weight", "delivered_weight")
    def _check_quantities(self):
        for rec in self:
            if rec.returned_weight > rec.total_measure:
                raise ValidationError("La cantidad retornada no puede ser mayor a la cantidad definida")
            elif (rec.delivered_weight + rec.returned_weight) > rec.total_measure:
                raise ValidationError(
                    "La cantidad entregada y la retornada no "
                    "puede ser mayor a la cantidad definida"
                )
            elif rec.delivered_weight > rec.total_measure:
                raise ValidationError("La cantidad entregada no puede exceder la cantidad definida")
    #endregion