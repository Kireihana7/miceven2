from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SalesByCustomerHsNationwide(models.TransientModel):
    _name = "sales.by.customer.hs.nationwide"

    currency_id = fields.Many2one(
        "res.currency",
        "Moneda",
        default=lambda self: self.env.company.currency_id
    )
    
    everything = fields.Boolean("Todo")
    importe_adeudado = fields.Boolean("Importe Adeudado")
    start_date = fields.Date("Fecha desde")
    end_date = fields.Date("Fecha hasta")
    partner_ids = fields.Many2many("res.partner", string="Clientes")
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    product_ids = fields.Many2many("product.product", string="Productos", domain=[('categ_id.complete_name', 'ilike', 'PRODUCTO TERMINADO'), ('uom_id.name', 'ilike', 'FD')])

    def get_invoice_domain(self):
        domain = [
            ("move_type", "=", "out_invoice"),
            ("company_id", "=", self.env.company.id),
            ("with_nc", "=", False),
            ("state", "=", "posted"),
            ("name", "not ilike", "promo"),
            ("amount_total", ">", 0),
        ]

        if not self.everything:
            domain += [
                ("invoice_date", ">=", self.start_date),
                ("invoice_date", "<=", self.end_date),
            ]

        if self.partner_ids:
            domain.append(("partner_id", "in", self.partner_ids.ids))
        else:
            domain.append(("partner_id", "!=", None))

        return domain

    # ================================================================================== #
    def action_print_report(self):
        domain = self.get_invoice_domain()

        invoices = self.env["account.move"] \
            .sudo() \
            .search(domain)

        # UPDATE: nuevo total.
        lines = invoices.invoice_line_ids.filtered(lambda x: x.product_id.categ_id and 'PRODUCTO TERMINADO' in x.product_id.categ_id.complete_name and 'FD' in x.product_id.uom_id.name)

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

        def callback(o): 
            return o.amount_total if o.currency_id == self.currency_id else o.amount_ref

        def callback_importe_adeudado(o): 
            return o.amount_residual if o.currency_id == self.currency_id else o.amount_residual_signed_ref

        # for partner in invoices.mapped('partner_id'): # <------ Otra forma de hacerlo.
        for partner in invoices.partner_id:
            qty_kg = 0
            partner_invoice = invoices.filtered(lambda i: i.partner_id == partner).invoice_line_ids.filtered(lambda x: x.product_id.categ_id and 'PRODUCTO TERMINADO' in x.product_id.categ_id.complete_name and 'FD' in x.product_id.uom_id.name)
            for line in partner_invoice:
                product_uom_id = line.product_uom_id
                quantity = line.quantity
                total_kg = quantity * product_uom_id.factor_inv
                qty_kg += total_kg

            datas.append({
                "state_id": partner.state_id.name if partner.state_id else '',
                "name": partner.name,
                "qty_fd": sum(invoices.filtered(lambda i: i.partner_id == partner).invoice_line_ids.filtered(lambda x: x.product_id.categ_id and 'PRODUCTO TERMINADO' in x.product_id.categ_id.complete_name and 'FD' in x.product_id.uom_id.name).mapped('quantity')),
                # "qty_kg": sum(invoices.filtered(lambda i: i.partner_id == partner).invoice_line_ids.mapped('sec_qty')),
                "qty_kg": qty_kg,
                "amount": sum(invoices.filtered(lambda i: i.partner_id == partner).mapped(callback)),
                "importe_adeudado": sum(invoices.filtered(lambda i: i.partner_id == partner).mapped(callback_importe_adeudado))
            })

        datas.sort(key=lambda u: u["amount"], reverse=True)
        
        # raise UserError(datas)
        total_qty_fd = 0
        total_qty_kg = 0
        index = 0
        for line in datas:
            index += 1
            total_qty_fd += line['qty_fd']
            total_qty_kg += line['qty_kg']

        # UPDATE: nuevo total.
        for product in lines.product_id:
            product_lines = lines.filtered(lambda l: l.product_id == product)

            for partner in product_lines.move_id.partner_id:
                user_lines = product_lines.filtered(lambda l: l.move_id.partner_id == partner)
                amount = sum(user_lines.mapped(lambda l: l.price_subtotal if l.currency_id == self.currency_id else l.price_subtotal_ref))
                total += amount

        # UPDATE: # Resumen de productos (Todos los productos):
        resumen_productos = []
        for product in lines.product_id.sorted(lambda x: x.name):
            product_lines = lines.filtered(lambda l: l.product_id == product)
            total_quantity = sum(product_lines.mapped("quantity"))
            total_amount = sum(product_lines.mapped(
                lambda l: l.price_subtotal if l.currency_id == self.currency_id else l.price_subtotal_ref))

            resumen_productos.append({
                'product_name': product.display_name,
                "total_quantity": total_quantity,
                "total_amount": total_amount,
            })

        return self.env.ref("eu_sales_kpi_kg.action_report_sales_by_customer_hs_nationwide") \
            .report_action([], data={
                "invoices": datas,
                # "total": sum(invoices.mapped(callback)),
                "total": total,
                "total_qty_fd": total_qty_fd,
                "total_qty_kg": total_qty_kg,
                "currency_id": self.currency_id.id,
                "start_date": self.start_date.strftime("%d/%m/%Y"),
                "end_date": self.end_date.strftime("%d/%m/%Y"),
                # UPDATE:
                "importe_adeudado": self.importe_adeudado,
                "total_importe_adeudado": sum(invoices.mapped(callback_importe_adeudado)),
                # UPDATE:
                'resumen_productos': resumen_productos
            })
