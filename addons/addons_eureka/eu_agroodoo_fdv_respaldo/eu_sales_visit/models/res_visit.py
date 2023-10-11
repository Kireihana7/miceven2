# -*- coding: utf-8 -*-

from datetime import date, datetime
from typing import List
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class ResVisit(models.Model):
    _name = 'res.visit'
    _description = 'Visita de cliente'
    _inherit = ['mail.thread', 'mail.activity.mixin']
        
    # Basic data
    name = fields.Char("Etiqueta", tracking=True)
    salesperson_id = fields.Many2one(
        "res.users", 
        "Vendedor", 
        tracking=True,
        related="partner_id.user_id",
        store=True,
    )
    partner_id = fields.Many2one("res.partner", "Cliente", tracking=True)
    duracion = fields.Float("Duración de la visita", tracking=True)
    fecha_visita = fields.Date("Fecha de visita", tracking=True)
    fecha_cancelacion = fields.Date("Fecha de cancelación", tracking=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id, tracking=True)
    status = fields.Selection([
        ("por_visitar", "Por visitar"),
        ("no_visitado", "No visitado"),
        ("visitando", "Visitando"),
        ("efectiva", "Efectiva"),
        ("no_efectiva", "No efectiva"),
    ], "Estatus", default="por_visitar", tracking=True)
    note = fields.Char("Nota", tracking=True)
    sale_order_id = fields.Many2one("sale.order", "Órden de venta", tracking=True)
    motivo_cancelacion = fields.Char("Motivo", tracking=True)
    client_due = fields.Monetary("Total adeudado", tracking=True)
    has_delay = fields.Boolean("Retrasados")
    tipo_visita = fields.Selection([
        ("toma_cliente", "Toma de cliente"),
        ("comercial", "Comercial"),
        ("cobranza", "Cobranza"),
    ], "Tipo de visita", default="comercial")

    # Order
    last_sale_order_id = fields.Many2one("sale.order", "Última orden", tracking=True)
    last_sale_order_date = fields.Datetime("Fecha de la órden", related="last_sale_order_id.date_order", tracking=True)
    last_sale_order_amount = fields.Monetary("Monto de la órden", related="last_sale_order_id.amount_total", tracking=True)

    # Repeting
    to_repeat = fields.Boolean("Repetir")
    frequency_id = fields.Many2one("res.visit.frequency", "Frecuencia", tracking=True)
    repeat_since = fields.Date("Repetir desde", default=fields.Date.context_today, tracking=True,)
    next_date = fields.Date("Próxima visita", compute="_compute_next_date", store=True, tracking=True,)

    # Recall
    to_recall = fields.Boolean("Recordar", tracking=True,)
    recall_date = fields.Datetime("Fecha de aviso", default=fields.Datetime.today, tracking=True,)

    #region Onchanges
    @api.onchange("partner_id", "salesperson_id")
    def _onchange_partner(self):
        for rec in self:
            partner = rec.partner_id

            if partner:
                if partner.default_frequency_id:
                    rec.frequency_id = partner.default_frequency_id

                if rec.salesperson_id:
                    rec.name = " ".join([
                        "Visita para", 
                        partner.name, 
                        "por", 
                        rec.salesperson_id.name,
                    ])
                    
    @api.onchange("to_repeat")
    def _onchange_to_repeat(self):
        for rec in self:
            if not rec.to_repeat:
                rec.fecha_visita = None
            else:
                rec.fecha_visita = rec.repeat_since

    @api.onchange("tipo_visita")
    def _onchange_tipo_visita(self):
        for rec in self:
            if rec.tipo_visita == "cobranza":
                rec.update({
                    "to_repeat": False,
                    "frequency_id": None,
                    "next_date": None,
                })

    @api.onchange("repeat_since")
    def _onchange_repeat_since(self):
        for rec in self:
            rec.fecha_visita = rec.repeat_since
    #endregion

    #region Actions
    def _action_set_no_visitado(self):
        self.env["res.visit"] \
            .search([("status", "=", "por_visitar")]) \
            .filtered(lambda v: v.fecha_visita < date.today()) \
            .action_set_status({"status": "no_visitado"})

    def action_open_status_wizard(self):
        status: str = self._context["status"]

        if not self.partner_id.state == "activo":
            raise UserError("El cliente debe estar activo")

        vals = {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "target": "new",
        }

        if status == "efectiva":
            vals.update({
                "name": "Visita efectiva",
                "res_model": "visita.efectiva",
            })
        else:
            vals.update({
                "name": "Visita no efectiva",
                "res_model": "visita.no.efectiva",
                "context": {
                    "default_state": status,
                }
            })

        return vals

    def action_set_status(self, context: dict={}):
        for rec in self.sudo():
            rec.status = context.get("status") or rec._context["status"]

            if (rec.status == "visitando") and (date.today() > rec.fecha_visita):
                rec.has_delay = True

            if (rec.to_repeat) and (rec.status not in ["por_visitar", "visitando"]):
                rec.copy({
                    "fecha_visita": rec.next_date,
                    "status": "por_visitar",
                    "client_due": rec.partner_id.sale_amount_due,
                    "last_sale_order_id": rec.partner_id.last_sale_order_id.id,
                })
         

    def _action_notify_user(self):
        visit_ids = self.env["res.visit"] \
            .search([("to_recall", "=", True),("recall_date", "!=", False)]) \
            .filtered(lambda v: v.recall_date == date.today())

        for visit in visit_ids:
            user_id = visit.salesperson_id

            visit.activity_schedule(
                "eu_sales_visit.mail_act_visitas",
                date.today(),
                summary="Tiene visitas pendientes",
                note=f"Tienes un recordatorio de tus visitas activo",
                user_id=user_id.id,
                request_partner_id=user_id.partner_id.id
            )

    def action_create_so(self):
        self.ensure_one()

        if self.sudo().tipo_visita == "cobranza":
            return

        partner_id = self.partner_id
        address = partner_id.address_get(['delivery', 'invoice'])

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                "default_user_id": self.salesperson_id.id,
                "default_partner_id": partner_id.id,
                "default_visit_id": self.id,
                "default_partner_invoice_id": address["delivery"],
                "default_partner_shipping_id": address["invoice"],
                "default_pricelist_id": partner_id.property_product_pricelist.id if partner_id.property_product_pricelist else False,
            },
        }
    #endregion

    @api.constrains("repeat_since")
    def _check_repeat_since(self):
        for rec in self.filtered("to_repeat"):
            frequency = rec.frequency_id

            if (frequency.repeat_every == "week") and (rec.repeat_since.weekday() not in map(int, frequency.weekday_ids.mapped("name"))):
                raise ValidationError("El campo 'repetir desde' no esta dentro de los dias de plazo")

    #region ORM
    @api.model
    def create(self, vals_list):
        if type(vals_list) == dict:
            vals_list: List[dict] = [vals_list]

        for val in vals_list:
            if self.search([
                ("partner_id", "=", val.get("partner_id")), 
                ("status", "in", ["por_visitar", "visitando"])
            ]):
                raise UserError("Ya hay una visita programada para este cliente")

        res = super().create(vals_list)

        for rec in res:
            rec.write({
                "client_due": rec.partner_id.sale_amount_due,
                "last_sale_order_id": rec.partner_id.last_sale_order_id.id,
            })

        return res

    def write(self, vals: dict):
        for rec in self:
            if vals.get("fecha_visita") and (rec.status != "por_visitar"):
                raise UserError("No puedes cambiar la fecha de visita después de visitar")

        return super().write(vals)
    #endregion

            
    @api.depends(
        "repeat_since", 
        "frequency_id", 
        "frequency_id.repeat_every", 
        "frequency_id.repeat_rate", 
        "frequency_id.weekday_ids",
    )
    def _compute_next_date(self):
        for rec in self.filtered("to_repeat"):
            frequency = rec.frequency_id

            rec.next_date: date = rec.fecha_visita or rec.repeat_since

            if frequency.repeat_every == "year":
                rec.next_date += relativedelta(years=frequency.repeat_rate)
            elif frequency.repeat_every == "month":
                rec.next_date += relativedelta(months=frequency.repeat_rate)
            elif frequency.repeat_every == "day":
                rec.next_date += relativedelta(days=frequency.repeat_rate)
            else:
                # Add n numbers of weeks
                if len(frequency.weekday_ids) == 1:
                    rec.next_date += relativedelta(weeks=frequency.repeat_rate)
                    continue

                days = list(map(int, frequency.weekday_ids.mapped("name")))
                repeat_day = rec.next_date.weekday()
                next_day = None

                # Establish the next day
                if repeat_day == days[-1]:
                    next_day = days[0]

                    if frequency.repeat_rate > 1:
                        rec.next_date += relativedelta(weeks=frequency.repeat_rate)
                else:
                    next_day = days[days.index(repeat_day) + 1]

                while rec.next_date.weekday() != next_day:
                    rec.next_date += relativedelta(days=1)