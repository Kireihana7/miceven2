# -*- coding: utf-8 -*-
# David Linarez 7

from odoo import models
from odoo.exceptions import UserError

class ReporteVendedoresVentas(models.TransientModel):
    _name = "reporte.vendedores.ventas"
    _description = "Reporte vendedores ventas"
    _inherit = "kaly.reporte"

    def action_print_report(self):
        super().action_print_report()
    
        domain = self.get_invoice_domain()

        invoices = self.env["account.move"] \
            .sudo() \
            .search(domain)

        # UPDATE: nuevo total.
        lines = invoices.invoice_line_ids.filtered(lambda x: x.product_id.categ_id and 'PRODUCTO TERMINADO' in x.product_id.categ_id.complete_name)
        # Todas las líneas sin filtrar por productos:
        lines_without_filter = lines

        # Filtro de productos:
        if self.product_ids:
            # Líneas:
            lines = lines.filtered(lambda l: l.product_id in self.product_ids)        
            # Facturas:
            invoices_ids = list(set(lines.mapped('move_id').ids))
            # raise UserError(invoices_ids)
            invoices = self.env['account.move'].sudo().search([('id', 'in', invoices_ids)])

        # UPDATE: nuevo total.
        total = 0

        if not invoices:
            raise UserError("No hay facturas")
        
        datas = []
        callback = lambda o: o.amount_total if o.currency_id == self.currency_id else o.amount_ref
        callback_importe_adeudado = lambda o: o.amount_residual if o.currency_id == self.currency_id else o.amount_residual_signed_ref

        for user in invoices.user_id:
            datas.append({
                "name": (user.employee_id.emp_id or "") + " " + user.name,
                "amount": sum(invoices.filtered(lambda i: i.user_id == user).mapped(callback)),
                "importe_adeudado": sum(invoices.filtered(lambda i: i.user_id == user).mapped(callback_importe_adeudado))
            })

        datas.sort(key=lambda u: u["amount"], reverse=True)
        
        # UPDATE: nuevo total.
        for product in lines.product_id:
            product_lines = lines.filtered(lambda l: l.product_id == product)

            for user in product_lines.move_id.user_id:
                user_lines = product_lines.filtered(lambda l: l.move_id.user_id == user)
                amount = sum(user_lines.mapped(lambda l: l.price_subtotal if l.currency_id == self.currency_id else l.price_subtotal_ref))
                total += amount

        # UPDATE: # Resumen de productos (Todos los productos):
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

        return self.env.ref("eu_account_reports.reporte_vendedores_ventas_action_report") \
            .report_action([], data={
                "invoices": datas,
                # "total": sum(invoices.mapped(callback)),
                "total": total,
                "currency_id": self.currency_id.id,
                "start_date": self.start_date.strftime("%d/%m/%Y"),
                "end_date": self.end_date.strftime("%d/%m/%Y"),
                # UPDATE:
                "importe_adeudado": self.importe_adeudado,
                "total_importe_adeudado": sum(invoices.mapped(callback_importe_adeudado)),
                # UPDATE:
                'resumen_productos': resumen_productos
            })
        