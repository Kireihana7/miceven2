# -*- coding: utf-8 -*-

from itertools import groupby
from odoo import models, fields, api
from odoo.exceptions import UserError

class HistoryPriceReport(models.TransientModel):
    _name = 'product.history.price.report'
    _description = "Reporte de historial de costo"

    start_date = fields.Date("Fecha desde")
    end_date = fields.Date("Fecha hasta")
    product_category_ids = fields.Many2many("product.category", string="Categorias")
    product_ids = fields.Many2many("product.product", string="Productos")
    all_products = fields.Boolean("Todos los productos")
    all_time = fields.Boolean("Todo el tiempo")

    @api.onchange("all_products")
    def _onchange_all_products(self):
        self.update({
            "product_category_ids": None,
            "product_ids": None,
        })

    @api.onchange("all_time")
    def _onchange_all_time(self):
        self.update({
            "start_date": None,
            "end_date": None,
        })

    def print_report(self):
        domain = []

        if not self.all_products:
            if not self.product_ids:
                raise UserError("Debes seleccionar un producto")

            domain.append(("product_tmpl_id","in",self.product_ids.product_tmpl_id.ids))

            if self.product_category_ids:
                domain.append(("product_category_id","in",self.product_category_ids.ids))

        if not self.all_time:
            domain.extend([
                ("create_date",">=",fields.Date.to_string(self.start_date)),
                ("create_date","<=",fields.Date.to_string(self.end_date)),
            ])

        history_ids = self.env["product.price.history"].sudo().search(domain).ids

        if not history_ids:
            raise UserError("No se encontró ningún registro en esas condiciones")

        return self.env.ref('eu_product_price_history.action_report_product_price_history').report_action(history_ids)