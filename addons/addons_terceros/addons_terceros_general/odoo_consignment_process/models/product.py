# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    custom_is_consignment = fields.Boolean(
        string='Is Consignment',
        copy= False
    )
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line',
        string="Purchase Line",
        readonly=True,
        copy=False,
    )
    custom_picking_id = fields.Many2one(
        'stock.picking',
        string="Consignment Picking",
        readonly=True,
        copy=False,
    ) #Old name picking_id

    sale_order_line_ids = fields.Many2many(
        'sale.order.line',
        string="Sale Order Line",
        readonly=True,
        copy=False,
    )
    sale_state = fields.Selection(
        selection=[
            ('sold','Sold'),
            ('not_sold','Not Sold'),
        ],
        default="not_sold",
        string='Consignment Status',
        compute="_consignment_sale_state",
        readonly=False,
    )
    total_available_qty = fields.Float(
        string="Total Available Qty",
        compute="_consignment_total_available_qty",
        store=True,
    )
    purchase_qty = fields.Float(
        string="Purchase Qty",
        compute="_consignment_purchase_qty",
        store=True,
        copy=False,
    )
    purchase_price = fields.Float(
        string="Purchase Price",
        readonly=True,
        copy=False,
    )
    purchase_price_total = fields.Float(
        string="Purchase Subtotal",
        compute="_consignment_purchase_price_total",
        store=True,
        copy=False,
    )
    sale_qty = fields.Float(
        string="Sale Qty",
        compute="_consignment_sale_qty",
        store=True,
    )
    sale_price_total = fields.Float(
        string="Sale Subtotal",
        compute="_consignment_sale_price_total",
        store=True,
    )
    purchase_order_line_ids = fields.One2many(
        'purchase.order.line',
        'product_id',
        string="Purchase Line",
        readonly=True,
        copy=False,
    )

    @api.depends()
    def _consignment_sale_state(self):
        for rec in self:
            if rec.total_available_qty <= 0.0:
                rec.sale_state = 'sold'
            else:
                rec.sale_state = 'not_sold'

    @api.depends('sale_qty','purchase_qty','purchase_order_line_ids','purchase_order_line_ids.product_qty', 'purchase_order_line_ids.state')
    def _consignment_total_available_qty(self):
        for rec in self:
            line_ids = rec.purchase_order_line_ids.filtered(lambda x: x.is_consignment and x.state in ['purchase', 'done'])
            total_product_qty = sum(line.product_qty for line in line_ids)
            rec.total_available_qty = total_product_qty - rec.sale_qty

    @api.depends('sale_order_line_ids', 'sale_order_line_ids.order_id.is_consignment', 'sale_order_line_ids.state', 'sale_order_line_ids.product_uom_qty')
    def _consignment_sale_qty(self):
        for rec in self:
            line_ids = rec.sale_order_line_ids.filtered(lambda x: x.order_id.is_consignment and x.state in ['sale', 'done'])
            total_sale_qty = sum(line.product_uom_qty for line in line_ids)
            rec.sale_qty = total_sale_qty

    @api.depends('sale_order_line_ids', 'sale_order_line_ids.order_id.is_consignment', 'sale_order_line_ids.state', 'sale_order_line_ids.price_subtotal', 'sale_order_line_ids.state')
    def _consignment_sale_price_total(self):
        for rec in self:
            line_ids = rec.sale_order_line_ids.filtered(lambda x: x.order_id.is_consignment and x.state in ['sale', 'done'])
            sale_price_total = sum(line.price_subtotal for line in line_ids)
            rec.sale_price_total = sale_price_total

    @api.depends('purchase_order_line_ids','purchase_order_line_ids.state', 'purchase_order_line_ids.price_subtotal')
    def _consignment_purchase_price_total(self):
        for rec in self:
            line_ids = rec.purchase_order_line_ids.filtered(lambda x: x.is_consignment and x.state in ['purchase', 'done'])
            rec.purchase_price_total = sum(line.price_subtotal for line in line_ids)

    @api.depends('purchase_order_line_ids','purchase_order_line_ids.state','purchase_order_line_ids.product_qty')
    def _consignment_purchase_qty(self):
        for rec in self:
            line_ids = rec.purchase_order_line_ids.filtered(lambda x: x.is_consignment and x.state in ['purchase', 'done'])
            rec.purchase_qty = sum(line.product_qty for line in line_ids)
