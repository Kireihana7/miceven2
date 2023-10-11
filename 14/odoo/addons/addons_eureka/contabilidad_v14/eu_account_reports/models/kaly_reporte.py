# -*- coding: utf-8 -*-
# David Linarez

from odoo import models, fields, api
from odoo.exceptions import UserError

class KalyReporte(models.AbstractModel):
    _name = "kaly.reporte"
    _description = "Reporte de kaly"

    currency_id = fields.Many2one(
        "res.currency",
        "Moneda",
        default=lambda self: self.env.company.currency_id
    )
    everything = fields.Boolean("Todo")
    importe_adeudado = fields.Boolean("Importe Adeudado")
    start_date = fields.Date("Fecha desde")
    end_date = fields.Date("Fecha hasta")
    user_ids = fields.Many2many("res.users", string="Vendedores")
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    # Se usará en el reporte 6 y 7:
    product_ids = fields.Many2many("product.product", string="Productos", domain=[('categ_id.complete_name', 'ilike', 'PRODUCTO TERMINADO')])
    
    def get_invoice_domain(self):
        domain = [
            ("move_type","=","out_invoice"),
            ("company_id","=",self.env.company.id),
            ("with_nc","=",False),
            ("state","=","posted"),
            ("name","not ilike","promo"),
            ("amount_total",">",0),
        ]
        
        if not self.everything:
            domain += [
                ("invoice_date",">=",self.start_date),
                ("invoice_date","<=",self.end_date),
            ]

        if self.user_ids:
            domain.append(("user_id","in",self.user_ids.ids))
        else:
            domain.append(("user_id","!=",None))

        return domain
    
    @api.onchange("everything")
    def _onchange_everything(self):
        self.update({
            "start_date": None,
            "end_date": None,
        })

    def action_print_report(self):
        if self.start_date > self.end_date:
            raise UserError("La fecha de inicio no puede ser menor a la fecha fin")