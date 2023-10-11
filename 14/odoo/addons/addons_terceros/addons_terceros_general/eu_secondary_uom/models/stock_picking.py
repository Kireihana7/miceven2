# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = "stock.move"
    
    sec_qty = fields.Float(string="Cantidad Sec.", digits=dp.get_precision('Product Unit of Measure'),readonly=True,compute="_compute_product_sec_uom_qty",store=True)
    sec_done_qty = fields.Float(string="Cantidad Sec. Hecha", digits=dp.get_precision('Product Unit of Measure'),readonly=True, compute='_compute_product_uom_done_qty', store=False,)
    sec_uom = fields.Many2one("uom.uom", string='UdM Secundaria',readonly=True,store=True)
    is_secondary_unit = fields.Boolean(string="¿Tiene Unidad Secundaria?", related="product_id.is_secondary_unit",readonly=True)

    @api.onchange('product_id')
    def onchange_product_id_sec(self):
        for rec in self:
            rec.sec_uom = False
            if rec.is_secondary_unit == True:
                rec.sec_uom = rec.product_id.product_tmpl_id.secondary_uom.id

    @api.onchange('quantity_done')
    def onchange_product_uom_done_qty(self):
        for rec in self:
            if rec and rec.is_secondary_unit == True and rec.sec_uom:
                rec.sec_done_qty = rec.product_uom._compute_quantity(rec.quantity_done, rec.sec_uom)

    @api.depends('quantity_done')
    def _compute_product_uom_done_qty(self):
        for x in self:
            x.sec_done_qty = 0.00
            x.onchange_product_uom_qty()
            if x and x.is_secondary_unit == True and x.sec_uom:
                x.sec_done_qty = x.product_uom._compute_quantity(x.quantity_done, x.sec_uom)
      
    @api.onchange('product_uom_qty', 'product_uom')
    def onchange_product_uom_qty(self):
        for rec in self:
            if rec and rec.is_secondary_unit == True and rec.sec_uom:
                rec.sec_qty = rec.product_uom._compute_quantity(rec.product_uom_qty, rec.sec_uom)
    
    @api.depends('product_uom_qty', 'product_uom','sec_uom')
    def _compute_product_sec_uom_qty(self):
        for rec in self:
            if rec and rec.is_secondary_unit == True and rec.sec_uom:
                rec.sec_qty = rec.product_uom._compute_quantity(rec.product_uom_qty, rec.sec_uom)

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        if res.sale_line_id and res.sale_line_id.is_secondary_unit == True and res.sale_line_id.sec_uom:
            res.update({'sec_uom':res.sale_line_id.sec_uom.id, 'sec_qty':res.sale_line_id.sec_qty})
        if res.purchase_line_id and res.purchase_line_id.is_secondary_unit == True and res.purchase_line_id.sec_uom:
            res.update({'sec_uom':res.purchase_line_id.sec_uom.id, 'sec_qty':res.purchase_line_id.sec_qty})
        return res

    
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    sec_qty = fields.Float("Cantidad Sec. Hecha.", digits=dp.get_precision('Product Unit of Measure'),readonly=True,compute="_compute_product_sec_uom_qty",store=True)
    sec_uom = fields.Many2one("uom.uom", 'UdM Secundaria', related="move_id.sec_uom",readonly=True)
    is_secondary_unit = fields.Boolean("¿Tiene unidad Secundaria?", related="move_id.product_id.is_secondary_unit",readonly=True)
    
    @api.onchange('qty_done')
    def onchange_product_uom_done_qty_move_line(self):
        for rec in self:
            if rec and rec.is_secondary_unit == True and rec.sec_uom:
                rec.sec_qty = rec.product_uom_id._compute_quantity(rec.qty_done, rec.sec_uom)
    
    @api.depends('product_uom_qty', 'product_uom_id','sec_uom')
    def _compute_product_sec_uom_qty(self):
        for rec in self:
            rec.sec_qty = 0.0
            if rec.is_secondary_unit == True and rec.sec_uom:
                rec.sec_qty = rec.product_uom_id._compute_quantity(rec.qty_done, rec.sec_uom)       
    #@api.onchange('sec_qty')
    #def onchange_product_sec_done_qty_move_line(self):
    #    if self and self.is_secondary_unit == True and self.sec_uom:
    #        self.qty_done = self.sec_uom._compute_quantity(self.sec_qty, self.product_uom_id)


class StockInmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    
    def process(self):
        res = super(StockInmediateTransfer, self).process()
        for picking_ids in self.pick_ids:
            for moves in picking_ids.move_lines:
                if moves.sec_uom:
                    moves.sec_done_qty = moves.product_uom._compute_quantity(moves.product_uom_qty, moves.sec_uom)
                for move_lines in moves.move_line_ids:
                    if move_lines.sec_uom:
                        move_lines.sec_qty = move_lines.product_uom_id._compute_quantity(move_lines.qty_done, moves.sec_uom)
        return res
    
