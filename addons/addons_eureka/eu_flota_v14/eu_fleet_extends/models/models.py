# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    fleet_service_id = fields.Many2one("fleet.vehicle.log.services", "Servicio")

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        service = self.env.context.get("default_fleet_service_id")

        if service:
            res.write({"fleet_service_id": service})
        
        for rec in res.filtered("picking_id.fleet_service_id"):
            rec.fleet_service_id = rec.picking_id.fleet_service_id

            if not rec.origin:
                rec.origin = rec.fleet_service_id.name

        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fleet_service_id = fields.Many2one("fleet.vehicle.log.services", "Servicio")

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    state = fields.Selection(selection_add=[("maintenance","Mantenimiento")])

class FleetVehicleLogService(models.Model):
    _inherit  = "fleet.vehicle.log.services"

    service_type = fields.Selection([
        ("external", "Externa"),
        ("internal", "Interna"),
    ], default="internal", string="Tipo de servicio", tracking=True)
    requisition_id = fields.Many2one("material.purchase.requisition", "Requisicion", tracking=True)
    picking_ids = fields.One2many("stock.picking", "fleet_service_id", "Transferencias")
    picking_count = fields.Integer("Transferencias", compute="_compute_picking_count")
    stock_move_ids = fields.One2many("stock.move", "fleet_service_id", "Movimientos")
    stock_move_count = fields.Integer("Movimientos", compute="_compute_stock_move_ids")
    total_cost = fields.Monetary("Costo total", compute="_compute_total_cost")

    @api.depends(
        "stock_move_ids.stock_valuation_layer_ids.value",
        "stock_move_ids.state",
    )
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = abs(sum(rec.stock_move_ids.filtered(lambda s: s.state == "done").stock_valuation_layer_ids.mapped("value")))

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        accounts = self.env['fleet.vehicle.log.services']

        for line in res:
            if '__domain' in line:
                accounts = self.search(line['__domain'])

            if 'total_cost' in fields:
                line['total_cost'] = sum(accounts.mapped('total_cost'))

        return res
    
    @api.onchange("service_type")
    def _onchange_service_type(self):
        self.update({"requisition_id": None})

    @api.constrains("state","service_type","requisition_id")
    def _check_service_state(self):
        for rec in self:
            if rec.service_type == "external" \
                and rec.state in ["done","cancel"] \
                and int(rec.requisition_id.state) < 5:
                raise ValidationError("No puedes cerrar el servicio si no has cerrado la requisición")

    @api.depends("picking_ids")
    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)

    @api.depends("stock_move_ids")
    def _compute_stock_move_ids(self):
        for rec in self:
            rec.stock_move_count = len(rec.stock_move_ids)

    def action_goto_stock_move(self):
        return {
            "name": "Movimientos",
            "type": 'ir.actions.act_window',
            "target": 'current',
            "res_model": "stock.move",
            "view_mode": "tree",
            "domain": [("id","in",self.stock_move_ids.ids)],
            "context": {
                "create": False,
                "delete": False,
                "edit": False,
            },
        }

    def action_goto_picking(self):
        return {
            "name": "Transferencias",
            "type": 'ir.actions.act_window',
            "target": 'current',
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id","in",self.picking_ids.ids)],
            "context": {
                "default_origin": self.name,
                "default_fleet_service_id": self.id,
                "default_partner_id": self.env.user.partner_id.id,
            },
        }

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    manual_odometer_since = fields.Datetime(tracking=True)
    manual_odometer = fields.Float("Odómetro manual", tracking=True)
    manual_odometer_maintenance = fields.Float("Mantenimiento según odómetro", tracking=True)
    odometer_start = fields.Float(tracking=True)

    def action_update_manual_odometer(self):
        for rec in self:
            if not rec.manual_odometer_since:
                continue 

            last_odometer = self.env["fleet.vehicle.odometer"] \
                .search([
                    ("vehicle_id","=",rec.id),
                    ("date", ">=", rec.manual_odometer_since)
                ], limit=1, order="value desc") \
                .value

            rec.manual_odometer = last_odometer - rec.odometer_start

            if rec.manual_odometer_maintenance and rec.manual_odometer >= rec.manual_odometer_maintenance:
                rec.action_notify_maintenance()

    def action_notify_maintenance(self):
        user = self.env.user

        for rec in self:
            message = self.env['mail.message'].sudo().create([{
                'subject': 'Mantenimiento de flota',
                'body': """
<a href="#" data-oe-id="{user_id}" data-oe-model="res.users">@{username}</a> 
El vehiculo {vehicle_id} precisa de un mantenimiento""".format(
    user_id=user.id, 
    username=user.name,
    vehicle_id=rec.name
),
                'author_id': user.partner_id.id,
                'email_from': user.email,
                'reply_to': user.email,
                'model': 'fleet.vehicle',
                'is_internal': True,
                'subtype_id': self.env.ref('mail.mt_note').id,
                'res_id': rec.id,
                'notification_ids': [
                    (0, 0, {
                        'res_partner_id': user.id,
                        'notification_type': 'inbox',
                    }),
                ],
            }])

            self.env['mail.mail'].sudo() \
                .create({
                    'mail_message_id': message.id,
                    'email_to': user.email,
                    'auto_delete': True,
                }) \
                .send(raise_exception=False)

            rec.activity_schedule(
                user_id=user.id,
                date_deadline=fields.Date.context_today(rec),
                summary='Mantenimiento de flota',
                note="El vehiculo {} precisa de un mantenimiento".format(rec.name),
            )

            rec.state = "maintenance"
        
    def action_stop_manual_odometer(self):
        self.write({
            "manual_odometer": 0, 
            "manual_odometer_since":  None,
            "odometer_start": 0
        })

    def action_reset_manual_odometer(self):
        self.write({
            "manual_odometer": 0, 
            "manual_odometer_since":  fields.Datetime.now(),
        })

        for rec in self:
            rec.odometer_start = rec.odometer

class FleetVehicleOdometer(models.Model):
    _inherit = "fleet.vehicle.odometer"

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        res.vehicle_id.action_update_manual_odometer()

        return res

    def write(self, vals):
        res = super().write(vals)

        self.vehicle_id.action_update_manual_odometer()

        return res
        

    def unlink(self):
        vehicle_id = self.vehicle_id

        res = super().unlink()

        vehicle_id.action_update_manual_odometer()

        return res
