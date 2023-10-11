# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    qty_no_dispatch = fields.Float(string="No Distpach Qty", compute="_compute_qty_dispatch")
    qty_to_dispatch = fields.Float(string="To Distpach Qty", compute="_compute_qty_dispatch")
    qty_on_stock    = fields.Float(string="Qty on Stock",compute="_compute_qty_on_stock")      
    
    def _compute_qty_dispatch(self):
        for rec in self:
            lineas = self.env['stock.picking']\
                .search([('state', '=', 'done'),('picking_type_id.code', '=', 'outgoing')]) \
                .move_ids_without_package \
                .filtered(lambda s: s.product_id.id == rec.id)
            rec.qty_no_dispatch = sum(lineas.filtered(lambda x: x.picking_id.dispatch_status == 'no_dispatch').mapped('quantity_done'))
            rec.qty_to_dispatch = sum(lineas.filtered(lambda x: x.picking_id.dispatch_status == 'to_dispatch').mapped('quantity_done'))

    @api.depends('qty_no_dispatch','qty_available','qty_to_dispatch')
    def _compute_qty_on_stock(self):
        for rec in self:
            rec.qty_on_stock = rec.qty_available + rec.qty_no_dispatch + rec.qty_to_dispatch