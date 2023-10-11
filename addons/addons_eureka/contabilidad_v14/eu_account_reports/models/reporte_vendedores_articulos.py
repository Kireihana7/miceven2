# -*- coding: utf-8 -*-
# David Linarez 8

from odoo import models, fields
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError

class ReporteVendedoresArticulo(models.TransientModel):
    _name = "reporte.vendedores.articulo"
    _description = "Reporte vendedores ventas"
    _inherit = "kaly.reporte"

    def action_print_report(self):
        super().action_print_report()

        domain = self.get_invoice_domain()

        lines = self.env["account.move"].search(domain).invoice_line_ids.filtered(lambda x: x.product_id.categ_id and 'PRODUCTO TERMINADO' in x.product_id.categ_id.complete_name)
        # Todas las líneas sin filtrar por productos:
        lines_without_filter = lines
        data = {}

        # Filtro de productos:
        if self.product_ids:
            lines = lines.filtered(lambda l: l.product_id in self.product_ids)

        filtered = lambda l: l.move_id.user_id
        lines = lines.sorted(filtered)
        total = 0

        if not lines:
            raise UserError("No hay lineas")
        
        for product in lines.product_id:
            users = {}
            product_lines = lines.filtered(lambda l: l.product_id == product)

            for user in product_lines.move_id.user_id:
                user_lines = product_lines.filtered(lambda l: l.move_id.user_id == user)
                amount = sum(user_lines.mapped(lambda l: l.price_subtotal if l.currency_id == self.currency_id else l.price_subtotal_ref))
                total += amount

                users[user.name] = {
                    "quantity": sum(user_lines.mapped("quantity")),
                    "uom": user_lines[0].product_uom_id.name,
                    "amount": amount,
                }

            data[product.display_name] = dict(sorted(users.items(), key=lambda user: user[1]["amount"], reverse=True))

        # Resumen de productos (Todos los productos):
        resumen_productos = []
        for product in lines.product_id.sorted(lambda x: x.name):
            product_lines = lines.filtered(lambda l: l.product_id == product)
            total_quantity = sum(product_lines.mapped("quantity"))
            total_amount = sum(product_lines.mapped(lambda l: l.price_subtotal if l.currency_id == self.currency_id else l.price_subtotal_ref))

            resumen_productos.append({
                'product_name': product.display_name,
                "total_quantity": total_quantity,
                "total_amount": total_amount,
            })
                                
        return self.env.ref("eu_account_reports.reporte_vendedores_articulos_action_report") \
            .report_action([], data={
                "datas": data,
                "total": total,
                "currency_id": self.currency_id.id,
                "start_date": self.start_date.strftime("%d/%m/%Y"),
                "end_date": self.end_date.strftime("%d/%m/%Y"),
                # UPDATE:
                'resumen_productos': resumen_productos
            })