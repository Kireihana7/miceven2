# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    mto_indicator = fields.Boolean('MTO', readonly=True, compute="_get_mto_indicator", store=True)


    @api.depends('product_id', 'warehouse_id')
    def _get_mto_indicator(self):
        for line in self:
            line.mto_indicator = False
            mrp_parameter = self.env["mrp.parameter"].search([
                ("product_id", "=", line.product_id.id),
                ("warehouse_id", "=", line.warehouse_id.id),
                ], limit=1)
            if mrp_parameter and mrp_parameter.demand_indicator == "20":
                line.mto_indicator = True

    def _check_buy(self):
        check_buy = False
        for line in self:
            product_routes = self.product_id.route_ids
            wh_buy_route = self.order_id.warehouse_id.buy_pull_id.route_id
        if not wh_buy_route:
            try:
                wh_buy_route = self.env['stock.warehouse']._find_global_route('stock.route_warehouse0_buy', _('Buy'))
            except UserError:
                pass
        if wh_buy_route and wh_buy_route in product_routes:
            check_buy = True
        else:
            check_buy = False
        return check_buy

    # sale_purchase module
    # propagate analytic account in PO Service
    def _purchase_service_prepare_line_values(self, purchase_order, quantity=False):
        values = super()._purchase_service_prepare_line_values(purchase_order=purchase_order, quantity=quantity)
        values.update({'account_analytic_id': self.order_id.analytic_account_id.id})
        return values


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mto_indicator = fields.Boolean('MTO', readonly=True, compute="_get_mto_indicator", store=True)


    @api.depends('order_line.mto_indicator')
    def _get_mto_indicator(self):
        for order in self:
            order.mto_indicator = False
            if any(line.mto_indicator for line in order.order_line):
                order.mto_indicator = True

    def button_create_analytic_account(self):
        for record in self:
            analytic_account = self.env['account.analytic.account'].create({
                    'name': record.name,
                    'partner_id': record.partner_id.id,
                })
            record.analytic_account_id = analytic_account.id

    def action_view_analytic_lines(self):
        self.ensure_one()
        analytic_lines_ids = self.analytic_account_id.line_ids.ids
        view_id = self.env.ref('mrp_planning_engine_mto.view_account_analytic_line_sales_order_tree').id
        action = {
            'res_model': 'account.analytic.line',
            'type': 'ir.actions.act_window',
            'name': _("Analytic Lines by %s", self.name),
            'domain': [('id', 'in', analytic_lines_ids)],
            'views': [(view_id, "tree"),(False, "form"),(False, "graph"),(False, "pivot")],
        }
        return action

    def action_confirm(self):
        super().action_confirm()
        for order in self:
            # checks on sale order items
            if order.mto_indicator:
                if any(line.product_id.type == 'consu' and line.price_unit != 0.0 for line in order.order_line):
                    raise UserError(_("MTO Sales are not allowed for consumable products, please set the price as zero"))
                if not order.analytic_account_id:
                    raise UserError(_("MTO Sale Order requires an Analytic Account"))
            # analytic account in delivery
            for line in order.order_line:
                if line.product_id.type == 'product':
                    #if line.mto_indicator and line._check_buy()
                    #    continue
                    #else:
                    line.move_ids.write({'analytic_account_id': order.analytic_account_id.id})

