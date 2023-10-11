from odoo import models, fields,api,_
from odoo.exceptions import UserError
from odoo.osv import expression


class purchaseOrder(models.Model):
    _inherit = "purchase.order"

    puesto_compra = fields.Boolean(string="Por puesto de Compra",tracking=True)
    productor = fields.Many2one('res.partner',string="Productor",tracking=True)
    zona_partner = fields.Many2one('partner.zone',string="Zona",tracking=True)

    @api.model
    def default_get(self, fields):
        res = super(purchaseOrder, self).default_get(fields)
        if self._context.get('puesto_compra'):
            res.update({
                'puesto_compra': True,
                'picking_type_id':self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', self.env.company.id),('puesto_compra','=',True)],limit=1).id,
                'currency_id':2,
            })
        #res['move_ids'] = 
        return res

    def button_confirm_full(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
            for pic in order.picking_ids:
                for lin in order.order_line:
                    # for line in pic.move_ids_without_package.filtered(lambda line: line.product_id.id == lin.product_id.id):
                    #     line.quantity_done = lin.product_qty
                        #line.lot_id = lin.lot_id.id
                    # for lines in pic.move_line_nosuggest_ids.filtered(lambda line: line.product_id.id == lin.product_id.id):
                    #     lines.qty_done = lin.product_qty
                    #     lines.lot_id = lin.lot_id.id
                    for lineas in pic.move_line_ids.filtered(lambda line: line.product_id.id == lin.product_id.id and not line.lot_id ):
                        lineas.qty_done = lin.product_qty
                        lineas.lot_id = lin.lot_id.id
                        break
                pic.action_confirm()
                if pic.state != 'cancel':
                    pic.with_context(cancel_backorder=True)._action_done()
        return True

    def action_view_products(self):
        if not self.partner_id:
            raise UserError(_('A customer should be set on the purchase order.'))

        self = self.with_company(self.company_id)

        domain = [
            ('purchase_ok', '=', True),
            '&',('invoice_policy', '=', 'delivery'), ('service_type', '=', 'manual'),
            '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False),
            #'|', ('categ_id.brach_id', '=', self.branch_id.id), ('categ_id.branch_id', '=', False)
            ]
        deposit_product = self.env['ir.config_parameter'].sudo().get_param('purchase.default_deposit_product_id')
        if deposit_product:
            domain = expression.AND([domain, [('id', '!=', deposit_product)]])

        kanban_view = self.env.ref('add_product_purchase_order.view_product_product_kanban_material')
        search_view = self.env.ref('add_product_purchase_order.product_search_form_view_inherit_knk')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Choose Products'),
            'res_model': 'product.product',
            'views': [(kanban_view.id, 'kanban'), (False, 'form')],
            'search_view_id': [search_view.id, 'search'],
            'domain': domain,
            'context': {
                # 'fsm_mode': True,
                #'create': self.env['product.template'].check_access_rights('create', raise_exception=False),
                'create': False,
                'purchase_order_id': self.id,  # avoid 'default_' context key as we are going to create SOL with this context
                #'pricelist': self.partner_id.property_product_pricelist.id,
                #'pricelist': self.pricelist_id.id,
                'hide_qty_buttons': self.state == 'done',
                'default_invoice_policy': 'delivery',
            },
            'help': _("""<p class="o_view_nocontent_smiling_face">
                            Create a new product
                        </p><p>
                            You must define a product for everything you sell or purchase,
                            whether it's a storable product, a consumable or a service.
                        </p>""")
        }