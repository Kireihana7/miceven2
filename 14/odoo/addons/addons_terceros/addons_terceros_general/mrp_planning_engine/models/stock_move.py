# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = 'stock.rule'

    # purchase_stock module
    def _make_po_get_domain(self, company_id, values, partner):
        return (("id", "=", 0),)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    mto_origin = fields.Char('MTO Origin', readonly=True)

    # purchase_stock module
    # create purchase order item with mto_origin
    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, company_id, values, po):
        res = super()._prepare_purchase_order_line_from_procurement(product_id, product_qty, product_uom, company_id, values, po)
        res.update({'mto_origin': values.get('mto_origin', False)})
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    reduced_qty = fields.Float("Demand Reduction Qty", digits='Product Unit of Measure', readonly=True, default=0.0, copy=False)

    @api.constrains('product_uom_qty')
    def _get_demand_reduction(self):
        for line in self:
            if line.reduced_qty > 0:
                raise UserError(_('it is not possible to change quantity item because reduction process already occurred.'))
        return True


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        for picking in self.picking_ids:
            for move in picking.move_lines.filtered(lambda r: r.state != 'cancel'):
                mrp_parameter = self.env["mrp.parameter"].search([('product_id', '=', move.product_id.id), ('warehouse_id', '=', move.warehouse_id.id)], limit=1)
                # strategies 40 and 50
                if mrp_parameter and move.sale_line_id and mrp_parameter.demand_indicator in ("40", "50"):
                    backward_days = mrp_parameter.mrp_demand_backward_day or 1
                    delivery_date = move.sale_line_id.order_id.commitment_date or move.sale_line_id.order_id.expected_date or move.sale_line_id.order_id.date_order
                    backward_date = delivery_date - timedelta(days=backward_days)
                    customer_location_id = move.sale_line_id.order_id.partner_id.with_company(move.company_id).property_stock_customer
                    if move.location_dest_id == customer_location_id:
                        backward_demand_items = self.env["mrp.demand"].search([
                            ('mrp_parameter_id', '=', mrp_parameter.id),
                            ('state', '=', 'done'),
                            ('date_planned', '<=', delivery_date),
                            ('date_planned', '>', backward_date)])
                        qty = move.product_qty
                        move._reduce_demand(qty, backward_demand_items)
        return res

    def action_cancel(self):
        for picking in self.picking_ids:
            for move in picking.move_lines.filtered(lambda r: r.state != 'cancel'):
                mrp_parameter = self.env["mrp.parameter"].search([('product_id', '=', move.product_id.id), ('warehouse_id', '=', move.warehouse_id.id)], limit=1)
                # strategies 40 and 50
                if mrp_parameter and move.sale_line_id and mrp_parameter.demand_indicator in ("40", "50"):
                    backward_days = mrp_parameter.mrp_demand_backward_day or 1
                    delivery_date = move.sale_line_id.order_id.commitment_date or move.sale_line_id.order_id.expected_date or move.sale_line_id.order_id.date_order
                    backward_date = delivery_date - timedelta(days=backward_days)
                    backward_demand_items = self.env["mrp.demand"].search([
                        ('mrp_parameter_id', '=', mrp_parameter.id),
                        ('state', '=', 'done'),
                        ('date_planned', '<=', delivery_date),
                        ('date_planned', '>', backward_date)]).sorted(key=lambda r: r.date_planned)
                    qty = move.product_qty
                    move._restore_demand(qty, backward_demand_items)
        return super().action_cancel()


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        res = super()._create_returns()
        for return_move in self.product_return_moves:
            move = return_move.move_id
            mrp_parameter = self.env["mrp.parameter"].search([('product_id', '=', move.product_id.id), ('warehouse_id', '=', move.warehouse_id.id)], limit=1)
            if mrp_parameter and move.sale_line_id:
                # strategies 40 and 50
                if mrp_parameter.demand_indicator in ("40", "50"):
                    backward_days = mrp_parameter.mrp_demand_backward_day or 1
                    delivery_date = move.sale_line_id.order_id.commitment_date or move.sale_line_id.order_id.expected_date or move.sale_line_id.order_id.date_order
                    backward_date = delivery_date - timedelta(days=backward_days)
                    customer_location_id = move.sale_line_id.order_id.partner_id.with_company(move.company_id).property_stock_customer
                    if move.location_dest_id == customer_location_id:
                        backward_demand_items = self.env["mrp.demand"].search([
                            ('mrp_parameter_id', '=', mrp_parameter.id),
                            ('state', '=', 'done'),
                            ('date_planned', '<=', delivery_date),
                            ('date_planned', '>', backward_date)]).sorted(key=lambda r: r.date_planned)
                        qty = return_move.quantity
                        move._restore_demand(qty, backward_demand_items)
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.constrains('state')
    def _get_demand_consumption(self):
        self._demand_consumption()
        return True

    def _demand_consumption(self):
        for move in self:
            mrp_parameter = self.env["mrp.parameter"].search([('product_id', '=', move.product_id.id), ('warehouse_id', '=', move.warehouse_id.id)], limit=1)
            if mrp_parameter and move.sale_line_id:
                # strategies 10 and 30
                if mrp_parameter.demand_indicator in ("10", "30"):
                    # delivery
                    if move.state == 'done' and move.picking_id.picking_type_id.code == 'outgoing':
                        fifo_demand_items = self.env["mrp.demand"].search([
                            ('mrp_parameter_id', '=', mrp_parameter.id),
                            ('state', '=', 'done')]).sorted(key=lambda r: r.date_planned)
                        qty = move.product_qty
                        move._reduce_demand(qty, fifo_demand_items)
                    # return
                    elif move.state == 'done' and move.picking_id.picking_type_id.code == 'incoming':
                        fifo_demand_items = self.env["mrp.demand"].search([
                            ('mrp_parameter_id', '=', mrp_parameter.id),
                            ('state', '=', 'done')])
                        qty = move.product_qty
                        move._restore_demand(qty, fifo_demand_items)
        return True

    def _restore_demand(self, qty, demand_items):
        for demand_item in demand_items:
            if qty > 0:
                if demand_item.planned_qty >= (demand_item.mrp_qty + qty):
                    demand_item.mrp_qty += qty
                    self.sale_line_id.reduced_qty =  0
                    qty = 0
                if demand_item.planned_qty < (demand_item.mrp_qty + qty):
                    self.sale_line_id.reduced_qty += - (demand_item.planned_qty -  demand_item.mrp_qty)
                    qty += - (demand_item.planned_qty - demand_item.mrp_qty)
                    demand_item.mrp_qty = demand_item.planned_qty
        return True

    def _reduce_demand(self, qty, demand_items):
        for demand_item in demand_items:
            if qty > 0:
                # riduzione parziale
                if qty >= demand_item.mrp_qty:
                    qty += - demand_item.mrp_qty
                    self.sale_line_id.reduced_qty += demand_item.mrp_qty
                    demand_item.mrp_qty = 0
                # capienza nell'item demand
                if qty < demand_item.mrp_qty:
                    demand_item.mrp_qty += - qty
                    self.sale_line_id.reduced_qty += qty
                    qty = 0
        return True
