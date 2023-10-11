# -*- coding: utf-8 -*-

from odoo import models, fields, api

class KalyReporte(models.AbstractModel):
    _name = "kaly.reporte"
    _description = "Reporte de kaly"

    currency_id = fields.Many2one(
        "res.currency",
        "Moneda",
        default=lambda self: self.env.company.currency_id
    )
    everything = fields.Boolean("Todo")
    start_date = fields.Date("Fecha desde")
    end_date = fields.Date("Fecha hasta")
    user_ids = fields.Many2many("res.users", string="Vendedores")

    @property
    def invoice_domain(self):
        return [
            ("move_type","=","out_invoice"),
            ("company_id","=",self.env.company.id),
            ("with_nc","=",False),
            ("state","=","posted"),
            ("name","not ilike","promo"),
            ("amount_total",">",0),
        ]
    
    @api.onchange("everything")
    def _onchange_everything(self):
        self.update({
            "start_date": None,
            "end_date": None,
        })

    def action_print_report(self):
        pass