# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class DeliveryNotesByProducts(models.TransientModel):
    _name = 'delivery.notes.by.products'

    date_start = fields.Datetime('Fecha Inicio')
    date_end = fields.Datetime('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    company_id = fields.Many2one('res.company', string='Compañia', required=True,
                                 default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('waiting', 'Esperando otra operación'),
        ('confirmed', 'Esperando'),
        ('assigned', 'Lista'),
        ('done', 'Hecho'),
        ('cancel', 'Cancelada'),
    ], string='Estatus', )

    def report_delivery_notes_by_products(self):
        product_ids = []
        products = []
        final = []
        estatus = ''
        domain =  [
            ('company_id', '=', self.company_id.id),
            ('picking_type_code', '=', 'outgoing'),
        ]
        
        if self.date_start:
            domain.append(('date_done', '>=', self.date_start))
        if self.date_end:
            domain.append(('date_done', '<=', self.date_end))
        if self.state:
            if self.state == 'draft':
                estatus = 'Borrador'
            elif self.state == 'waiting':
                estatus = 'Esperando otra operación'
            elif self.state == 'confirmed':
                estatus = 'Esperando otra operación'
            elif self.state == 'assigned':
                estatus = 'Lista'
            elif self.state == 'done':
                estatus = 'Hecho'
            elif self.state == 'cancel':
                estatus = 'Cancelada'

            domain.append(('state', '=', self.state))

        stock_picking = self.env['stock.picking'].search(domain)
            
        if len(stock_picking)==0:
            raise UserError(_("No hay datos para imprimir"))
        picking_existe = False
        for row in stock_picking.move_ids_without_package.sorted(key=lambda m: m.picking_id.id):
            if row.product_id.id not in product_ids:
                product_ids.append(row.product_id.id)
            if picking_existe != row.picking_id.id:
                final.append({
                    'product_id': row.product_id.id,
                    'product_name': row.product_id.name,
                    'unidad_medida': row.product_uom.name,
                    'cantidad': sum(stock_picking.move_ids_without_package.filtered(lambda x: x.picking_id.id == row.picking_id.id).mapped('quantity_done')),
                    'name_fac': row.picking_id.name,
                    'fecha': row.picking_id.date_done,
                    'cliente': row.partner_id.name,
                    'stock_id': row.id,
                })
            picking_existe = row.picking_id.id
        #raise UserError(final)
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
            'date_start': self.date_start.date() if self.date_start else '',
            'date_end': self.date_end.date() if self.date_end else '',
            'partner_id_vat': self.partner_id.vat if self.partner_id.vat else '',
            'partner_id_name': self.partner_id.name if self.partner_id.name else '',
        }
        
        data = {
            'form': res,
        }

        return self.env.ref('eu_delivery_notes_by_products.delivery_notes_by_products_report').report_action(self, data=data)
