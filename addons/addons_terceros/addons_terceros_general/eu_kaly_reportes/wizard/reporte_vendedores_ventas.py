# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import UserError

class ReporteVendedoresVentas(models.TransientModel):
    _name = "reporte.vendedores.ventas"
    _description = "Reporte vendedores ventas"
    _inherit = "kaly.reporte"

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

        invoices = self.env["account.move"] \
            .sudo() \
            .search(domain)

        if not invoices:
            raise UserError("No hay facturas")
        
        datas = []
        callback = lambda o: o.amount_total if o.currency_id == self.currency_id else o.amount_ref

        for user in invoices.user_id:
            datas.append({
                "name": (user.employee_id.emp_id or "") + " " + user.name,
                "amount": sum(invoices.filtered(lambda i: i.user_id == user).mapped(callback))
            })

        datas.sort(key=lambda u: u["amount"], reverse=True)
        
        return self.env.ref("eu_kaly_reportes.reporte_vendedores_ventas_action_report") \
            .report_action([], data={
                "invoices": datas,
                "total": sum(invoices.mapped(callback)),
                "currency_id": self.currency_id.id,
                "start_date": self.start_date,
                "end_date": self.end_date,
            })
        