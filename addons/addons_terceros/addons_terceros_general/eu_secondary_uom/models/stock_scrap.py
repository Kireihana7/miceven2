# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class StockScrap(models.Model):
    _inherit = 'stock.scrap'
    
    sec_qty = fields.Float("Secondary Qty", digits=dp.get_precision('Product Unit of Measure'),readonly=True)
    sec_uom = fields.Many2one("uom.uom", 'Secondary UOM',readonly=True)
    is_secondary_unit = fields.Boolean('¿Tiene unidad Secundaria?', related='product_id.is_secondary_unit',readonly=True)
    secondary_category_id = fields.Many2one(related="product_uom_id.category_id", string="Categoría Sec",readonly=True )

    @api.onchange('scrap_qty', 'product_uom_id')
    def onchange_product_uom_qty(self):
        for rec in self:
            if rec and rec.is_secondary_unit == True and rec.sec_uom:
                rec.sec_qty = rec.product_uom_id._compute_quantity(rec.scrap_qty, rec.sec_uom)

    #@api.onchange('sec_qty', 'sec_uom')
    #def onchange_sec_qty(self):
    #    if self and self.is_secondary_unit == True and self.product_uom_id:
    #        self.scrap_qty = self.sec_uom._compute_quantity(self.sec_qty, self.product_uom_id)

    @api.onchange('product_id')
    def onchange_secondary_uom(self):
        for rec in self:
            if rec.product_id.is_secondary_unit == True and rec.product_id.uom_id:
                rec.sec_uom = rec.product_id.secondary_uom.id
