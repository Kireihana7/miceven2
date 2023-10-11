# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_order_ids = fields.One2many('pos.order', 'account_move')
    pos_payment_ids = fields.One2many('pos.payment', 'account_move_id')

    def _stock_account_get_last_step_stock_moves(self):
        stock_moves = super(AccountMove, self)._stock_account_get_last_step_stock_moves()
        for invoice in self.filtered(lambda x: x.move_type == 'out_invoice'):
            stock_moves += invoice.sudo().mapped('pos_order_ids.picking_ids.move_ids').filtered(lambda x: x.state == 'done' and x.location_dest_id.usage == 'customer')
        for invoice in self.filtered(lambda x: x.move_type == 'out_refund'):
            stock_moves += invoice.sudo().mapped('pos_order_ids.picking_ids.move_ids').filtered(lambda x: x.state == 'done' and x.location_id.usage == 'customer')
        return stock_moves


<<<<<<< HEAD
    def _get_invoiced_lot_values(self):
        self.ensure_one()

        lot_values = super(AccountMove, self)._get_invoiced_lot_values()

        if self.state == 'draft':
            return lot_values

        # user may not have access to POS orders, but it's ok if they have
        # access to the invoice
        for order in self.sudo().pos_order_ids:
            for line in order.lines:
                lots = line.pack_lot_ids or False
                if lots:
                    for lot in lots:
                        lot_values.append({
                            'product_name': lot.product_id.name,
                            'quantity': line.qty if lot.product_id.tracking == 'lot' else 1.0,
                            'uom_name': line.product_uom_id.name,
                            'lot_name': lot.lot_name,
                        })

        return lot_values

    def _compute_payments_widget_reconciled_info(self):
        """Add pos_payment_name field in the reconciled vals to be able to show the payment method in the invoice."""
        super()._compute_payments_widget_reconciled_info()
        for move in self:
            if move.invoice_payments_widget:
                if move.state == 'posted' and move.is_invoice(include_receipts=True):
                    reconciled_partials = move._get_all_reconciled_invoice_partials()
                    for i, reconciled_partial in enumerate(reconciled_partials):
                        counterpart_line = reconciled_partial['aml']
                        pos_payment = counterpart_line.move_id.sudo().pos_payment_ids
                        move.invoice_payments_widget['content'][i].update({
                            'pos_payment_name': pos_payment.payment_method_id.name,
                        })
=======
    def _tax_tags_need_inversion(self, move, is_refund, tax_type):
        # POS order operations are handled by the tax report just like invoices ;
        # we should never invert their tags.
        # Don't take orders or sessions without move.
        if move.move_type == 'entry' and move._origin.id:
            orders_count = self.env['pos.order'].search_count([('account_move', '=', move._origin.id)])
            sessions_count = self.env['pos.session'].search_count([('move_id', '=', move._origin.id)])
            if orders_count + sessions_count:
                return False
        return super()._tax_tags_need_inversion(move, is_refund, tax_type)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()
        if not self.product_id:
            return self.price_unit
        price_unit = super(AccountMoveLine, self)._stock_account_get_anglo_saxon_price_unit()
        sudo_order = self.move_id.sudo().pos_order_ids
        if sudo_order:
            price_unit = sudo_order._get_pos_anglo_saxon_price_unit(self.product_id, self.move_id.partner_id.id, self.quantity)
        return price_unit
<<<<<<< HEAD
=======

    def _get_not_entry_condition(self, aml):
        # Overridden so that sale entry moves created par POS still have their amount inverted
        # in _compute_tax_audit()
        rslt = super()._get_not_entry_condition(aml)

        sessions_count = self.env['pos.session'].search_count([('move_id', '=', aml.move_id.id)])
        pos_orders_count = self.env['pos.order'].search_count([('account_move', '=', aml.move_id.id)])

        return rslt or (sessions_count + pos_orders_count)

    def _get_refund_tax_audit_condition(self, aml):
        # Overridden so that the returns can be detected as credit notes by the tax audit computation
        rslt = super()._get_refund_tax_audit_condition(aml)

        if aml.move_id.is_invoice():
            # We don't need to check the pos orders for this move line if an invoice
            # is linked to it ; we know that the invoice type tells us whether it's a refund
            return rslt

        sessions_count = self.env['pos.session'].search_count([('move_id', '=', aml.move_id.id)])
        pos_orders_count = self.env['pos.order'].search_count([('account_move', '=', aml.move_id.id)])

        return rslt or (sessions_count + pos_orders_count and aml.debit > 0)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
