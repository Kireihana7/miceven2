# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    category_id = fields.Many2one(related="uom_id.category_id", string="Categoría", )
    secondary_uom_onhand = fields.Float(string='A Mano', compute='get_secondary_unit_on_hand_qty')
    secondary_uom_forecasted = fields.Float(string='Previsto', compute='get_secondary_unit_forecasted_qty')

    def get_secondary_unit_on_hand_qty(self):
        if self:
            for rec in self:
                if rec.secondary_uom:
                    rec.secondary_uom_onhand = rec.uom_id._compute_quantity(rec.qty_available, rec.secondary_uom)
                else:
                    rec.secondary_uom_onhand = 0
    
    #@api.multi
    def get_secondary_unit_forecasted_qty(self):
        if self:
            for rec in self:
                if rec.secondary_uom:
                    rec.secondary_uom_forecasted = rec.uom_id._compute_quantity(rec.virtual_available, rec.secondary_uom)
                else:
                    rec.secondary_uom_forecasted = 0
    def action_open_quants_second(self):
        domain = [('product_id', 'in', self.ids)]
        hide_location = not self.user_has_groups('stock.group_stock_multi_locations')
        hide_lot = all(product.tracking == 'none' for product in self)
        self = self.with_context(
            hide_location=hide_location, hide_lot=hide_lot,
            no_at_date=True, search_default_on_hand=True,
        )

        # If user have rights to write on quant, we define the view as editable.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_ids=self.product_tmpl_id.ids)
        action = self.env['stock.quant']._get_quants_action_secondary(domain)
        action["name"] = _('Update Quantity')
        return action

    def action_product_forecast_report_second(self):
        action = self.env.ref('stock.report_stock_quantity_action_product').read()[0]
        action['domain'] = [
            ('product_id', '=', self.id),
            ('warehouse_id', '!=', False),
        ]
        return action

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    secondary_uom = fields.Many2one('uom.uom', string='UdM Secundaria')
    secondary_uom_onhand = fields.Float(string='A Mano', compute='get_secondary_unit_on_hand_qty')
    secondary_uom_forecasted = fields.Float(string='Previsto', compute='get_secondary_unit_forecasted_qty')
    secondary_uom_name = fields.Char(related='secondary_uom.name', string="UdM Secundaria")
    is_secondary_unit = fields.Boolean(string="¿Tiene Unidad Secundaria?")
    secondary_category_id = fields.Many2one(related="uom_id.category_id",string="Categoría Sec", )



    #@api.multi
    def get_secondary_unit_on_hand_qty(self):
        if self:
            for rec in self:
                if rec.secondary_uom:
                    rec.secondary_uom_onhand = rec.uom_id._compute_quantity(rec.qty_available, rec.secondary_uom)
                else:
                    rec.secondary_uom_onhand = 0
    
    #@api.multi
    def get_secondary_unit_forecasted_qty(self):
        if self:
            for rec in self:
                if rec.secondary_uom:
                    rec.secondary_uom_forecasted = rec.uom_id._compute_quantity(rec.virtual_available, rec.secondary_uom)
                else:
                    rec.secondary_uom_forecasted = 0

    def action_product_forecast_report_second(self):
        action = self.env.ref('stock.report_stock_quantity_action_product').read()[0]
        action['domain'] = [
            ('product_id', '=', self.id),
            ('warehouse_id', '!=', False),
        ]
        return action


    def action_open_quants_second(self):
        domain = [('product_id', 'in', self.ids)]
        hide_location = not self.user_has_groups('stock.group_stock_multi_locations')
        hide_lot = all(product.tracking == 'none' for product in self)
        self = self.with_context(
            hide_location=hide_location, hide_lot=hide_lot,
            no_at_date=True, search_default_on_hand=True,
        )

        # If user have rights to write on quant, we define the view as editable.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_ids=self.product_tmpl_id.ids)
        action = self.env['stock.quant']._get_quants_action_secondary(domain)
        action["name"] = _('Update Quantity')
        return action


    #@api.multi
    def action_open_quants_second(self):
        return self.with_context(active_test=False).product_variant_ids.filtered(lambda p: p.active or p.qty_available != 0).action_open_quants_second()


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    secondary_unit_qty = fields.Float(compute="_compute_secondary_qty", string="A Mano", )
    secondary_unit = fields.Many2one(related='product_id.secondary_uom', string='UdM Secundaria', )
    secondary_unit_reserved_qty = fields.Float(compute="_compute_secondary_qty", string="A Mano", )
    secondary_unit_available_qty = fields.Float(compute="_compute_available_quantity_secondary", string="A Mano", )

    @api.depends('quantity','product_id','product_id.secondary_uom','reserved_quantity')
    def _compute_secondary_qty(self):
        for rec in self:
            rec.secondary_unit_qty = 0.0
            if rec.product_id.secondary_uom and rec.product_id.is_secondary_unit:
                rec.secondary_unit_qty = rec.product_id.uom_id._compute_quantity(rec.quantity,rec.product_id.secondary_uom)
            rec.secondary_unit_reserved_qty=0.0
            if rec.product_id.secondary_uom and rec.product_id.is_secondary_unit:
                rec.secondary_unit_reserved_qty = rec.product_id.uom_id._compute_quantity(rec.reserved_quantity,rec.product_id.secondary_uom)

    @api.depends('secondary_unit_qty', 'secondary_unit_reserved_qty')
    def _compute_available_quantity_secondary(self):
        for quant in self:
            quant.secondary_unit_available_qty = quant.secondary_unit_qty - quant.secondary_unit_reserved_qty

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        if 'secondary_unit_qty' not in fields :
            return super(StockQuant, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(StockQuant, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['secondary_unit_qty'] = sum(quant.secondary_unit_qty for quant in quants)
        return res


    @api.model
    def _get_quants_action_secondary(self, domain=None, extend=False):
        """ Returns an action to open quant view.
        Depending of the context (user have right to be inventory mode or not),
        the list view will be editable or readonly.

        :param domain: List for the domain, empty by default.
        :param extend: If True, enables form, graph and pivot views. False by default.
        """
        self._quant_tasks()
        ctx = dict(self.env.context or {})
        ctx.pop('group_by', None)
        action = {
            'name': _('Stock On Hand'),
            'view_type': 'tree',
            'view_mode': 'list,form',
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain or [],
            'help': """
                <p class="o_view_nocontent_empty_folder">No Stock On Hand</p>
                <p>This analysis gives you an overview of the current stock
                level of your products.</p>
                """
        }

        target_action = self.env.ref('stock.dashboard_open_quants', False)
        if target_action:
            action['id'] = target_action.id

        if self._is_inventory_mode():
            action['view_id'] = self.env.ref('eu_secondary_uom.view_stock_quant_tree_secondary_editable').id
            form_view = self.env.ref('eu_secondary_uom.view_stock_quant_form_secondary_editable').id
        else:
            action['view_id'] = self.env.ref('eu_secondary_uom.view_stock_quant_tree_secondary').id
            form_view = self.env.ref('eu_secondary_uom.view_stock_quant_form_secondary').id
        action.update({
            'views': [
                (action['view_id'], 'list'),
                (form_view, 'form'),
            ],
        })
        if extend:
            action.update({
                'view_mode': 'tree,form,pivot,graph',
                'views': [
                    (action['view_id'], 'list'),
                    (form_view, 'form'),
                    (self.env.ref('eu_secondary_uom.view_stock_quant_pivot_secondary').id, 'pivot'),
                    (self.env.ref('eu_secondary_uom.stock_quant_view_graph_secondary').id, 'graph'),
                ],
            })
        return action