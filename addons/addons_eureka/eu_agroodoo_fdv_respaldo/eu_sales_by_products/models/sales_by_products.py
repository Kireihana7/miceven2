# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class SalesByProducts(models.TransientModel):
    _name = 'sales.by.products'

    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    company_id = fields.Many2one('res.company', string='Compañia', required=True,
                                 default=lambda self: self.env.company)
    state = fields.Selection(selection=[
            ('draft', 'Borrador'),
            ('posted', 'Publicadas'),
        ], string='Estatus',
        default='posted')

    journal_id = fields.Many2one('account.journal', string='Diarios', domain="[('type', '=', 'sale')]")

    def report_sales_by_products(self):
        product_ids = []
        products = []
        final = []
        estatus = ''
        domain =  [
            ('company_id', '=', self.company_id.id),
            ('move_id.move_type', '=', 'out_invoice')]

        if self.journal_id:
            domain.append(('move_id.journal_id', '=', self.journal_id.id))
        if self.date_start:
            domain.append(('move_id.date', '>=', self.date_start))
        if self.date_end:
            domain.append(('move_id.date', '<=', self.date_end))
        if self.state:
            if self.state == 'draft':
                estatus = 'Borrador'
            elif self.state == 'posted':
                estatus = 'Publicadas'
            domain.append(('move_id.state', '=', self.state))

        account_move_line = self.env['account.move.line'].search(domain)
            
        if len(account_move_line)==0:
            raise UserError(_("No hay datos para imprimir"))

        for row in account_move_line:
            if row.product_id.id not in product_ids and row.product_id.id != False:
                product_ids.append(row.product_id.id)

            payment_term = 'contado'
            if row.move_id.invoice_date_due > row.move_id.invoice_date:
                payment_term = 'credito'

            final.append({
                'product_id': row.product_id.id,
                'product_name': row.product_id.name,
                'cantidad': row.quantity,
                'precio_unitario': row.price_unit,
                'precio_subtotal': row.price_subtotal,
                'precio_total': row.price_total,
                'unidad_medida': row.product_uom_id.name,
                'name_fac': row.move_id.name,
                'cliente': row.partner_id.name,
                'payment_term': payment_term,
                'date': row.move_id.date,
                'estatus': 'Borrador' if row.move_id.state == 'draft' else 'Publicada',
                })

        product_template = self.env['product.product'].search([('id','in',product_ids)])

        for x in product_template:
            products.append({
                'product_name':x.name,
                'product_id':x.id,
                })

        res = {
            'ids': self.ids,
            'model': self._name,
            'products': products,
            'estatus': estatus,
            'invoices': final,
            'date_start': self.date_start if self.date_start else '',
            'date_end': self.date_end if self.date_end else '',
            'partner_id_vat': self.partner_id.vat if self.partner_id.vat else '',
            'partner_id_name': self.partner_id.name if self.partner_id.name else '',
            'journal_id': self.journal_id.name if self.journal_id else '',
        }
        
        data = {
            'form': res,
        }

        return self.env.ref('eu_sales_by_products.sales_by_products_report').report_action(self, data=data)
