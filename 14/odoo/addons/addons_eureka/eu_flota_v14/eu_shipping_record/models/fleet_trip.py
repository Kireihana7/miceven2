# -*- coding: utf-8 -*-

from datetime import date, timedelta
from itertools import groupby
from typing import List
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class FleetTripType(models.Model):
    _name = 'fleet.trip.type'
    _description = 'Viajes'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Tipo", tracking=True,)
    product_id = fields.Many2one("product.product", "Producto", tracking=True, ondelete="cascade")

class FleetTripValidation(models.Model):
    _name = 'fleet.trip.validation'
    _description = 'Viajes'

    name = fields.Selection([
        ("en_proceso", "En Proceso"),
        ("finalizado", "Finalizado"),
        ("cancelado", "Cancelado"),
    ], "Validación de estatus")
    checked = fields.Boolean("Validado")
    employee_id = fields.Many2one("hr.employee", "Usuario validador")
    validation_date = fields.Datetime("Fecha de validación")
    fleet_trip_id = fields.Many2one('fleet.trip', "Viaje", ondelete="cascade")

    @api.onchange("checked")
    def _onchange_validation_date(self):
        for rec in self:
            if rec.checked:
                rec.update({
                    "validation_date": fields.Datetime.to_string(
                        fields.Datetime.context_timestamp(rec, (fields.Datetime.now() + timedelta(hours=4)))
                    ),
                })
            else:
                rec.update({"validation_date": None,})

class FleetTrip(models.Model):
    _name = 'fleet.trip'
    _description = 'Viajes'
    _inherit = 'fleet.trip.route'

    name = fields.Char("Título del viaje", tracking=True,)
    vehicle_id = fields.Many2one(
        "fleet.vehicle", 
        "Vehículo", 
        tracking=True, 
        ondelete="cascade"
    )
    user_is_manager = fields.Boolean(
        default=lambda self: self.env.user.has_group('eu_fleet_group.fleet_supervisor_group'),
        store=False,
    )
    branch_id = fields.Many2one("res.branch", "Sucursal", tracking=True,)
    origin_branch_id = fields.Many2one(compute="_compute_route", store=True)
    origin_city_id = fields.Many2one(compute="_compute_route", store=True)
    destination_branch_id = fields.Many2one(compute="_compute_route", store=True)
    destination_city_id = fields.Many2one(compute="_compute_route", store=True)
    route_type = fields.Selection(compute="_compute_route", store=True)
    shipping_date = fields.Datetime("Fecha de despacho", tracking=True,)
    state = fields.Selection([
        ("planificado", "Planificado"),
        ("en_proceso", "En Proceso"),
        ("finalizado", "Finalizado"),
        ("facturado", "Facturado"),
        ("cancelado", "Cancelado"),
    ], "Estatus", default="planificado", tracking=True,)
    state_with_invoice = fields.Selection(related="state")
    state_without_invoice = fields.Selection(related="state")
    line_ids = fields.One2many("fleet.trip.line", "fleet_trip_id", "Productos", tracking=True,)
    shipping_weight = fields.Float(
        "Kilos iniciales a despachar", 
        compute="_compute_shipping_weight",
        tracking=True,
    )
    shipped_weight = fields.Float(
        "Kilos despachados", 
        compute="_compute_shipped_weight",
        tracking=True,
    )
    orden_despacho = fields.Char("N° de consolidacion de carga", tracking=True)
    observation = fields.Text("Observación", tracking=True)
    numero_clientes = fields.Integer("N° de clientes", tracking=True,)
    leave_date = fields.Datetime("Fecha de salida", tracking=True,)
    arrive_date = fields.Datetime("Fecha de llegada", tracking=True,)
    type_id = fields.Many2one("fleet.trip.type", "Tipo de servicio", tracking=True, ondelete="restrict")
    partner_id = fields.Many2one("res.partner", "Cliente", tracking=True,)
    milestone_ids = fields.Many2many(
        "fleet.trip.milestone", 
        "fleet_trip_milestone_rel", 
        "trip_id", 
        "milestone_id", 
        "Zonas",
        tracking=True,
    )
    invoice_id = fields.Many2one("account.move", "Factura", tracking=True)

    # Related from vehicle_id
    driver_id = fields.Many2one("res.partner", "Conductor", tracking=True)
    driver_cedula = fields.Char("Cédula del conductor", related="driver_id.cedula", tracking=True,)
    license_plate = fields.Char("Placa", related="vehicle_id.license_plate", tracking=True,)
    initial_odometer = fields.Float("Odómetro inicial", tracking=True,)
    initial_fuel = fields.Float("Combustible inicial", tracking=True,)
    weight_limit = fields.Float("Capacidad del vehículo", related="vehicle_id.weight_limit", tracking=True)
    traveled = fields.Float("Recorrido", compute="_compute_traveled", tracking=True,)
    odometer_ids = fields.One2many("fleet.vehicle.odometer", "fleet_trip_id", "Ódometro", tracking=True)
    odometer_count = fields.Integer("Odómetros", compute="_compute_odometer_count", tracking=True,)
    fuel_log_ids = fields.One2many(
        "fleet.fuel.log",
        "fleet_trip_id",
        "Registros de combustible", 
        tracking=True,
    )
    fuel_log_count = fields.Integer("Registros de combustible", compute="_compute_fuel_log_count", tracking=True)

    # Return
    fecha_cancelacion = fields.Date("Fecha de cancelación", tracking=True,)
    motivo_cancelacion = fields.Text("Motivo de cancelación", tracking=True,)
    returned_line_ids = fields.One2many(
        "fleet.trip.return.line",
        "fleet_trip_id",
        "Línea devuelta",
        tracking=True,
    )

    # Viáticos
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.ref("base.VEF"))
    fleet_trip_validation_ids = fields.One2many("fleet.trip.validation", "fleet_trip_id", "Validaciones", tracking=True)
    fleet_viaticum_id = fields.Many2one("viaticum.viaticum", "Viático asociado", tracking=True)
    balance = fields.Monetary("Balance", related="fleet_viaticum_id.balance")
    can_invoice_trip = fields.Boolean(
        default=lambda self: bool(self.env["ir.config_parameter"].sudo().get_param("eu_shipping_record.can_invoice_trip")),
        store=False,
    )

    cost = fields.Monetary("Costo", tracking=True)
    has_picking = fields.Boolean("Tiene picking", tracking=True)
    picking_guide_id = fields.Many2one("guide.consolidate", "Picking", tracking=True)
    remaining_weight = fields.Float(compute="_compute_remaining_weight")

    #region Onchanges
    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        for rec in self:
            vehicle = rec.vehicle_id

            if not vehicle:
                continue

            rec.update({
                "driver_id": vehicle.driver_id,
                "initial_odometer": vehicle.odometer,
                "initial_fuel": vehicle.current_fuel,
            })

    @api.onchange("has_picking")
    def _onchange_has_picking(self):
        self.update({"picking_guide_id": None})

    #endregion

    #region Constrains
    @api.constrains("fleet_viaticum_id")
    def _check_fleet_viaticum_id(self):
        for rec in self.filtered("fleet_viaticum_id"):
            if self.search([("id","!=",rec.id),("fleet_viaticum_id","=",rec.fleet_viaticum_id.id),("state","!=","cancelado")]):
                raise ValidationError("Los viáticos no se pueden repetir")

    @api.constrains("shipping_weight", "weight_limit")
    def _check_weights(self):
        for rec in self:
            if rec.shipping_weight > rec.weight_limit:
                raise ValidationError("La cantidad de kilos a despachar excede los límites del vehículo") 
    #endregion

    #region Actions
    def action_get_parameter(self):
        return bool(self.env["ir.config_parameter"].sudo().get_param("eu_shipping_record.can_invoice_trip"))

    def action_set_state(self, context: dict={}):
        STATE = self._context.get("state", context.get("state"))

        for rec in self:
            if not rec.milestone_ids:
                raise UserError("Debes tener al menos un tabulador para comenzar el viaje")

        if STATE != "planificado": 
            for rec in self:
                validation = rec.fleet_trip_validation_ids.filtered(lambda v: v.name == STATE)

                if not validation.checked:
                    raise UserError("Debes validar antes de proceder")

            if STATE == "en_proceso":
                rec.cost = rec.milestone_ids.sorted("cost")[-1].cost if rec.milestone_ids else 0
        else:
            self.fleet_trip_validation_ids.write({
                "validation_date": None,
                "employee_id": None,
                "checked": False,
            })

        self.write({"state": STATE})

    def action_cancel_trip(self):
        self.write({
            "fecha_cancelacion": date.today(),
            "state": "cancelado",
        })

    def action_report_trip_driver(self):
        return self.env \
            .ref("eu_shipping_record.custom_action_report_trip_driver") \
            .report_action(self)

    def action_create_invoice(self):
        if not all(state == "finalizado" for state in self.mapped("state")):
            raise UserError("Los viajes deben estar finalizados para facturarse")
            
        if self.filtered("invoice_id"):
            raise UserError("Ciertos viajes ya están facturados")

        if len(self.partner_id) > 1:
            raise UserError("Sólo puedes facturar muchos viajes por el mismo cliente")

        if len(self.branch_id) > 1:
            raise UserError("Sólo puedes facturar muchos viajes por la misma sucursal")

        vals = self._get_move_line_vals()

        move_id = self.env["account.move"].create({
            "partner_id": self.partner_id.id,
            "move_type": "out_invoice",
            "invoice_date": date.today(),
            "company_id": self.env.company.id,
            "branch_id": self.branch_id.id,
        })

        for val in vals:
            val["move_id"] = move_id.id

        self.env["account.move.line"] \
            .with_context(check_move_validity=False) \
            .create(vals)

        move_id \
            .with_context(check_move_validity=False) \
            ._onchange_partner_id()

        self.write({
            "invoice_id": move_id.id,
            "state": "facturado",
        })

        return {
            "name": "Factura",
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": move_id.id,
        }

    def action_do_transhipment(self):
        return {
            "name": "Transbordo",
            "type": "ir.actions.act_window",
            "res_model": "do.transhipment",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_fleet_trip_id": self.id
            },
        }

    def action_create_odometer(self):
        self.ensure_one()

        context = self._get_readonly_context()

        context.update({
            "default_vehicle_id": self.vehicle_id.id,
            "default_fleet_trip_id": self.id,
            "default_date": fields.Date.today(),
            "default_driver_id": self.driver_id.id,
        })

        return {
            "name": "Odómetros",
            "type": "ir.actions.act_window",
            "res_model": "fleet.vehicle.odometer",
            "view_mode": "tree",
            "domain": [("fleet_trip_id", "=", self.id)],
            "context": context,
        }

    def action_create_fuel_log(self):
        self.ensure_one()

        context = self._get_readonly_context()

        context.update({
            "default_vehicle_id": self.vehicle_id.id,
            "default_fleet_trip_id": self.id,
        })

        return {
            "name": "Registros de combustible",
            "type": "ir.actions.act_window",
            "res_model": "fleet.fuel.log",
            "view_mode": "tree,form",
            "domain": [("fleet_trip_id", "=", self.id)],
            "context": context,
        }

    #endregion

    #region Helpers
    def _get_readonly_context(self) -> dict:
        self.ensure_one()

        context = {}

        if self.state in ["planificado", "cancelado"]:
            context.update({
                "create": 0,
                "delete": 0,
                "duplicate": 0,
                "edit": 0,
            })

        return context

    def _get_move_line_vals(self) -> List[dict]:
        vals = []

        for type_id, trip_ids in groupby(self, key=lambda rec: rec.type_id):
            trip_ids = self.browse([trip.id for trip in trip_ids])
            product_id = type_id.product_id
            price = round(sum(trip_ids.mapped(lambda t: sum(t.milestone_ids.mapped("cost")))), 4)

            vals.append({
                "name": type_id.name,
                "product_id": product_id.id,
                "quantity": 1,
                "credit": price,
                "debit": 0,
                "product_uom_id": product_id.uom_id.id,
                "sec_uom": product_id.secondary_uom.id,
                "price_unit": price,
                "account_id": product_id.categ_id.property_account_income_categ_id.id,
            })

        return vals
    #endregion

    #region Computes
    @api.depends("weight_limit","shipping_weight")
    def _compute_remaining_weight(self):
        for rec in self:
            rec.remaining_weight = rec.weight_limit - rec.shipping_weight

    @api.depends(
        "milestone_ids",
        "milestone_ids.route_type",
        "milestone_ids.origin_branch_id",
        "milestone_ids.origin_city_id",
        "milestone_ids.destination_branch_id",
        "milestone_ids.destination_city_id",
    )
    def _compute_route(self):
        for rec in self:
            if not rec.milestone_ids:
                rec.origin_branch_id =\
                rec.origin_city_id =\
                rec.destination_branch_id =\
                rec.destination_city_id =\
                rec.route_type = False

                continue

            first_milestone, last_milestone = rec.milestone_ids[0], rec.milestone_ids[-1]

            rec.origin_branch_id = first_milestone.origin_branch_id
            rec.origin_city_id = first_milestone.origin_city_id
            rec.destination_branch_id = last_milestone.destination_branch_id
            rec.destination_city_id = last_milestone.destination_city_id
            
            if rec.origin_city_id and rec.destination_city_id:
                rec.route_type = "city_city"
            elif rec.origin_branch_id and rec.destination_branch_id:
                rec.route_type = "branch_branch"
            elif rec.origin_city_id and rec.destination_branch_id:
                rec.route_type = "city_branch"
            else:
                rec.route_type = "branch_city"

    @api.depends("milestone_ids.cost")
    def _compute_cost(self):
        for rec in self:
            rec.cost = rec.milestone_ids.sorted("cost")[-1].cost if rec.milestone_ids else 0

    @api.depends("line_ids.delivered_weight", "has_picking", "picking_guide_id.total")
    def _compute_shipped_weight(self):
        for rec in self:
            if not rec.has_picking:
                rec.shipped_weight = sum(rec.line_ids.mapped("delivered_weight"))
            else:
                rec.shipped_weight = rec.picking_guide_id.total
            
    @api.depends("odometer_ids.value")
    def _compute_traveled(self):
        for rec in self:
            if rec.odometer_ids:
                rec.traveled = rec.odometer_ids.sorted("value", reverse=True)[0].value
            else:
                rec.traveled = 0

    @api.depends("line_ids.weight", "line_ids.quantity", "has_picking", "picking_guide_id.total_weight")
    def _compute_shipping_weight(self):
        for rec in self:
            if not rec.has_picking:
                rec.shipping_weight = sum(rec.line_ids.mapped("total_measure"))
            else:
                rec.shipping_weight = rec.picking_guide_id.total_weight

    @api.depends("odometer_ids")
    def _compute_odometer_count(self):
        for rec in self:
            rec.odometer_count = len(rec.odometer_ids)
            
    @api.depends("fuel_log_ids")
    def _compute_fuel_log_count(self):
        for rec in self:
            rec.fuel_log_count = len(rec.fuel_log_ids)
    #endregion

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        Sequence = self.env["ir.sequence"]
        CODE = "fleet.trip.sequence"
        COMPANY = self.env.company

        if not Sequence.search([("code", "=", CODE),("company_id", "=", COMPANY.id)]):
            Sequence.create({
                "code": CODE,
                "prefix": "TRIP/",
                'name': f"Viajes de {COMPANY.name}",
                'padding': 6,
                'company_id': COMPANY.id,
            })
        
        for rec in res:
            rec.name = Sequence.next_by_code(CODE)
            for state in ["en_proceso","finalizado","cancelado"]:
                rec.fleet_trip_validation_ids.create({
                    "name": state,
                    "fleet_trip_id": rec.id,
                })

        return res