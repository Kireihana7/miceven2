from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
import re
from datetime import datetime

class SalesByMonthProductsWizard(models.TransientModel):
    _name = "sales.by.month.products"

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
    product_ids = fields.Many2many("product.product", string="Productos", domain=[
                                   ('categ_id.complete_name', 'ilike', 'PRODUCTO TERMINADO')])

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

    def get_invoices_by_product_category(self, invoices, category_name):
        lines = invoices.invoice_line_ids.filtered(lambda x: x.product_id.categ_id and category_name in x.product_id.categ_id.complete_name)
        invoices_ids = list(set(lines.mapped('move_id').ids))
        invoices = self.env['account.move'].sudo().search([('id', 'in', invoices_ids)])  
        return invoices

    # ================================================================================== #
    def action_print_report(self):
        domain = self.get_invoice_domain()

        invoices = self.env["account.move"].sudo().search(domain)
        invoices_harina_maiz = self.get_invoices_by_product_category(invoices, 'PRODUCTO TERMINADO / HARINA')
        invoices_subproducto = self.get_invoices_by_product_category(invoices, 'PRODUCTO TERMINADO / SUBPRODUCTO')
        invoices_venta_azucar = self.get_invoices_by_product_category(invoices, 'PRODUCTO TERMINADO / AZUCAR')
        invoices_otros_productos = self.get_invoices_by_product_category(invoices, 'PRODUCTOS EN PROCESO / RESIDUO')

        # Líneas:
        domain.remove(("invoice_date", ">=", self.start_date))
        domain.remove(("invoice_date", "<=", self.end_date))

        # Obtener el año actual
        anio_actual = datetime.now().year
        # Crear la fecha del 1 de enero
        fecha_inicio = datetime(anio_actual, 1, 1).date()
        # Crear la fecha del 31 de diciembre
        fecha_fin = datetime(anio_actual, 12, 31).date()
        domain.append(("invoice_date", ">=", fecha_inicio))
        domain.append(("invoice_date", "<=", fecha_fin))
        # raise UserError(domain)
        invoices_all_year = self.env["account.move"].sudo().search(domain)
        lines = invoices_all_year.invoice_line_ids.filtered(lambda x: x.product_id.categ_id and 'PRODUCTO TERMINADO' in x.product_id.categ_id.complete_name)
        resumen_productos = []
        for product in lines.product_id.sorted(lambda x: x.name):
            product_lines = lines.filtered(lambda l: l.product_id == product)
            total_quantity = sum(product_lines.mapped("quantity"))
            total_amount = sum(product_lines.mapped(lambda l: l.price_subtotal if l.currency_id == self.currency_id else l.price_subtotal_ref)) or 0

            resumen_productos.append({
                'product_name': product.display_name,
                "total_quantity": total_quantity,
                "total_amount": total_amount,
            })

        return self.env.ref("eu_sales_kpi_kg.action_report_sales_by_month_products") \
            .report_action([], data={
                "start_date": self.start_date.strftime("%d/%m/%Y"),
                "end_date": self.end_date.strftime("%d/%m/%Y"),
                # ==================================================================================== #
                'enero_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 1 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 1 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'enero_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 1 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 1 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'enero_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 1 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 1 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'enero_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 1 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 1 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'febrero_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 2 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 2 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'febrero_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 2 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 2 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'febrero_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 2 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 2 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'febrero_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 2 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 2 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'marzo_harina_maiz': round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 3 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 3 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'marzo_subproducto': round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 3 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 3 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'marzo_venta_azucar': round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 3 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 3 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'marzo_otros_productos': round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 3 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 3 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'abril_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 4 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 4 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'abril_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 4 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 4 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'abril_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 4 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 4 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'abril_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 4 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 4 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'mayo_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 5 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 5 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'mayo_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 5 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 5 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'mayo_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 5 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 5 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'mayo_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 5 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 5 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'junio_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 6 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 6 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'junio_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 6 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 6 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'junio_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 6 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 6 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'junio_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 6 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 6 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'julio_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 7 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 7 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'julio_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 7 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 7 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'julio_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 7 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 7 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'julio_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 7 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 7 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'agosto_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 8 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 8 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'agosto_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 8 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 8 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'agosto_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 8 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 8 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'agosto_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 8 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 8 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'septiembre_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 9 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 9 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'septiembre_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 9 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 9 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'septiembre_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 9 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 9 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'septiembre_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 9 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 9 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'octubre_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 10 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 10 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'octubre_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 10 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 10 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'octubre_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 10 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 10 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'octubre_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 10 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 10 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'noviembre_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 11 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 11 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'noviembre_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 11 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 11 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'noviembre_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 11 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 11 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'noviembre_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 11 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 11 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,

                'diciembre_harina_maiz':round(sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 12 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_harina_maiz.filtered(lambda x: int(x.invoice_date.month) == 12 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_harina_maiz else 0,
                'diciembre_subproducto':round(sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 12 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_subproducto.filtered(lambda x: int(x.invoice_date.month) == 12 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_subproducto else 0,
                'diciembre_venta_azucar':round(sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 12 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_venta_azucar.filtered(lambda x: int(x.invoice_date.month) == 12 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_venta_azucar else 0,
                'diciembre_otros_productos':round(sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 12 and x.currency_id == x.company_id.currency_id).mapped('amount_total')) + sum(invoices_otros_productos.filtered(lambda x: int(x.invoice_date.month) == 12 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4) if invoices_otros_productos else 0,
            
                'resumen_productos': resumen_productos
            })