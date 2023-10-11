# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MergePurchaseOrder(models.TransientModel):
    _name = 'merge.requisition.order'
    _description = 'Merge Purchase Order'
    merge_type = \
        fields.Selection([
            ('new_cancel',
                'Create new order and cancel all selected purchase orders'),
            ('new_delete',
             'Create new order and delete all selected purchase orders'),
            ('merge_cancel',
             'Merge order on existing selected order and cancel others'),
            ('merge_delete',
                'Merge order on existing selected order and delete others')],
            default='new_cancel')
    purchase_order_id = fields.Many2one('purchase.requisition', 'Requisition Order')

    @api.onchange('merge_type')
    def onchange_merge_type(self):
        res = {}
        for order in self:
            order.purchase_order_id = False
            if order.merge_type in ['merge_cancel', 'merge_delete']:
                purchase_orders = self.env['purchase.requisition'].browse(
                    self._context.get('active_ids', []))
                res['domain'] = {
                    'purchase_order_id':
                    [('id', 'in',
                        [purchase.id for purchase in purchase_orders])]
                }
            return res

    def merge_orders(self):
        purchase_orders = self.env['purchase.requisition'].browse(
            self._context.get('active_ids', []))
        existing_po_line = False
        if len(self._context.get('active_ids', [])) < 2:
            raise UserError(
                _('Please select atleast two purchase orders to perform '
                    'the Merge Operation.'))
        if any(order.state != 'draft' for order in purchase_orders):
            raise UserError(
                _('Please select Purchase orders which are in RFQ state '
                  'to perform the Merge Operation.'))
        partner = purchase_orders[0].user_id.id
        if any(order.user_id.id != partner for order in purchase_orders):
            raise UserError(
                _('Please select Purchase orders whose Vendors are same to '
                    ' perform the Merge Operation.'))
        if self.merge_type == 'new_cancel':
            po = self.env['purchase.requisition'].with_context({
                'trigger_onchange': True,
                'onchange_fields_to_trigger': [partner]
            }).create({'user_id': partner})
            default = {'requisition_id': po.id}
            for order in purchase_orders:
                for line in order.line_ids:
                    existing_po_line = False
                    if po.line_ids:
                        for poline in po.line_ids:
                            if line.product_id == poline.product_id and\
                                    line.price_unit == poline.price_unit:
                                existing_po_line = poline
                                break
                    if existing_po_line:
                        existing_po_line.product_qty += line.product_qty
                    else:
                        line.copy(default=default)
            for order in purchase_orders:
                order.action_cancel()
        elif self.merge_type == 'new_delete':
            po = self.env['purchase.requisition'].with_context({
                'trigger_onchange': True,
                'onchange_fields_to_trigger': [partner]
            }).create({'user_id': partner})
            default = {'requisition_id': po.id}
            for order in purchase_orders:
                for line in order.order_line:
                    existing_po_line = False
                    if po.order_line:
                        for po_line in po.order_line:
                            if line.product_id == po_line.product_id and \
                                    line.price_unit == po_line.price_unit:
                                existing_po_line = po_line
                                break
                    if existing_po_line:
                        existing_po_line.product_qty += line.product_qty
                    else:
                        line.copy(default=default)
            for order in purchase_orders:
                order.sudo().action_cancel()
                order.sudo().unlink()
        elif self.merge_type == 'merge_cancel':
            default = {'requisition_id': self.purchase_order_id.id}
            po = self.purchase_order_id
            for order in purchase_orders:
                if order == po:
                    continue
                for line in order.order_line:
                    existing_po_line = False
                    if po.order_line:
                        for po_line in po.order_line:
                            if line.product_id == po_line.product_id and \
                                    line.price_unit == po_line.price_unit:
                                existing_po_line = po_line
                                break
                    if existing_po_line:
                        existing_po_line.product_qty += line.product_qty
                    else:
                        line.copy(default=default)
            for order in purchase_orders:
                if order != po:
                    order.sudo().action_cancel()
        else:
            default = {'requisition_id': self.purchase_order_id.id}
            po = self.purchase_order_id
            for order in purchase_orders:
                if order == po:
                    continue
                for line in order.order_line:
                    existing_po_line = False
                    if po.order_line:
                        for po_line in po.order_line:
                            if line.product_id == po_line.product_id and \
                                    line.price_unit == po_line.price_unit:
                                existing_po_line = po_line
                                break
                    if existing_po_line:
                        existing_po_line.product_qty += line.product_qty
                    else:
                        line.copy(default=default)
            for order in purchase_orders:
                if order != po:
                    order.sudo().action_cancel()
                    order.sudo().unlink()
