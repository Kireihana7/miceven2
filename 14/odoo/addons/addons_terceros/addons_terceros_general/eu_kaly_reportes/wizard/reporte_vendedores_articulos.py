# -*- coding: utf-8 -*-

from itertools import groupby
from odoo import models, fields
from odoo.exceptions import UserError

class ReporteVendedoresArticulo(models.TransientModel):
    _name = "reporte.vendedores.articulo"
    _description = "Reporte vendedores ventas"
    _inherit = "kaly.reporte"

    product_ids = fields.Many2many("product.product", string="Productos")

    def action_print_report(self):
        domain = self.invoice_domain

        if not self.everything:
            domain += [
                ("invoice_date",">=",self.start_date),
                ("invoice_date","<=",self.end_date),
            ]

        if self.user_ids:
            domain.append(("user_id","in",self.user_ids.ids))
        else:
            domain.append(("user_id","!=",None))


        lines = self.env["account.move"].search(domain).invoice_line_ids
        data = {}

        if self.product_ids:
            lines = lines.filtered(lambda l: l.product_id in self.product_ids)

        filtered = lambda l: l.move_id.user_id
        lines = lines.sorted(filtered)
        total = 0

        if not lines:
            raise UserError("No hay lineas")
        
        for product in lines.product_id:
            users = {}
            
            for user, move_line in groupby(lines.filtered(lambda l: l.product_id == product), key=filtered):
                move_line = self.env["account.move.line"].browse(l.id for l in move_line)
                amount = sum(move_line.mapped(lambda l: l.price_subtotal if l.currency_id == self.currency_id else l.price_subtotal_ref))
                total += amount

                users[user.name] = {
                    "quantity": sum(move_line.mapped("quantity")),
                    "uom": move_line[0].product_uom_id.name,
                    "amount": amount,
                }

            data[product.display_name] = dict(sorted(users.items(), key=lambda user: user[1]["amount"], reverse=True))

        return self.env.ref("eu_kaly_reportes.reporte_vendedores_articulos_action_report") \
            .report_action([], data={
                "datas": data,
                "total": total,
                "currency_id": self.currency_id.id,
                "start_date": self.start_date,
                "end_date": self.end_date,
            })