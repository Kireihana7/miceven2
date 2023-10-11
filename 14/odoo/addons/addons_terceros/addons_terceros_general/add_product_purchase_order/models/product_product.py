from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_quantity = fields.Integer('Quantity', compute="_compute_purchase_quantity", inverse="_inverse_purchase_quantity", search="_search_purchase_quantity")
    is_puesto_compra = fields.Boolean(string="Producto para Puesto de Compra")
    
    @api.depends_context('purchase_order_id')
    def _compute_purchase_quantity(self):
        order = self._get_contextual_sorder()
        if order:
            purchaseOrderLine = self.env['purchase.order.line']
            # if self.user_has_groups('project.group_project_user'):
            #     order = order.sudo()
            #     purchaseOrderLine = purchaseOrderLine.sudo()

            products_qties = purchaseOrderLine.read_group([('id', 'in', order.order_line.ids)], ['product_id', 'product_uom_qty'], ['product_id'])
            qty_dict = dict([(x['product_id'][0], x['product_uom_qty']) for x in products_qties if x['product_id']])
            for product in self:
                product.purchase_quantity = qty_dict.get(product.id, 0)
        else:
            self.purchase_quantity = False

    def _inverse_purchase_quantity(self):
        order = self._get_contextual_sorder()
        if order:
            for product in self:
                purchase_lines = self.env['purchase.order.line'].search([('order_id', '=', order.id), ('product_id', '=', product.id)])
                all_editable_lines = purchase_lines.filtered(lambda l: l.product_qty == 0 or l.qty_received_method == 'manual' or l.state != 'done')
                diff_qty = product.purchase_quantity - sum(purchase_lines.mapped('product_uom_qty'))

                if all_editable_lines:  # existing line: change ordered qty (and delivered, if delivered method)
                    if diff_qty > 0:
                        vals = {
                            'product_uom_qty': all_editable_lines[0].product_uom_qty + diff_qty,
                        }
                        if product.service_type == 'manual':
                            vals['product_qty'] = all_editable_lines[0].product_uom_qty + diff_qty
                        all_editable_lines[0].with_context(fsm_no_message_post=True).write(vals)
                        continue
                    # diff_qty is negative, we remove the quantities from existing editable lines:
                    for line in all_editable_lines:
                        new_line_qty = max(0, line.product_uom_qty + diff_qty)
                        diff_qty += line.product_uom_qty - new_line_qty
                        vals = {
                            'product_uom_qty': new_line_qty
                        }
                        if product.service_type == 'manual':
                            vals['product_qty'] = new_line_qty
                        line.write(vals)
                        if diff_qty == 0:
                            break

                elif diff_qty > 0:  # create new SOL
                    vals = {
                        'order_id': order.id,
                        'product_id': product.id,
                        'product_uom_qty': diff_qty,
                        'product_uom': product.uom_id.id
                    }
                    if product.service_type == 'manual':
                        vals['product_qty'] = diff_qty

                    # if order.pricelist_id.discount_policy == 'without_discount':
                    #     sol = self.env['purchase.order.line'].new(vals)
                    #     sol._onchange_discount()
                    #     vals.update({'discount': sol.discount or 0.0})
                    self.env['purchase.order.line'].create(vals)

    @api.model
    def _search_purchase_quantity(self, operator, value):
        if not (isinstance(value, int) or (isinstance(value, bool) and value is False)):
            raise ValueError('Invalid value: %s' % (value))
        if operator not in ('=', '!=', '<=', '<', '>', '>=') or (operator == '!=' and value is False):
            raise ValueError('Invalid operator: %s' % (operator))

        order = self._get_contextual_sorder()
        if not order:
            return []
        op = 'inselect'
        if value is False:
            value = 0
            operator = '>='
            op = 'not inselect'
        query = """
            SELECT product_id
            FROM purchase_order_line sol
            WHERE order_id = %s AND product_uom_qty {} %s
        """.format(operator)
        return [('id', op, (query, (order.id, value)))]

    @api.model
    def _get_contextual_sorder(self):
        order_id = self.env.context.get('purchase_order_id')
        if order_id:
            return self.env['purchase.order'].browse(int(order_id))
        return self.env['purchase.order']

    def set_purchase_quantity(self, quantity):
        values = []
        purchaseorder = self.env['purchase.order'].browse(self.env.context.get('active_ids'))
        for product in self:
            line = purchaseorder.order_line.filtered(lambda x: x.product_id == product)
            if not line:
                values.append((0, 0, {'product_id': product.id, 'product_uom_qty': quantity}))
                purchaseorder.order_line = values
            if line:
                if quantity <= 0.00:
                    line.unlink()
                else:
                    line.update({'product_uom_qty': quantity})
        self.purchase_quantity = quantity
        return True

    def purchase_add_quantity(self):
        return self.set_purchase_quantity(self.sudo().purchase_quantity + 1)

    def purchase_remove_quantity(self):
        return self.set_purchase_quantity(self.sudo().purchase_quantity - 1)
