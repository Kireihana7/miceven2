# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    sec_qty = fields.Float("Cantidad Sec.", digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    sec_uom = fields.Many2one("uom.uom", string='UdM Secundaria',readonly=True)
    is_secondary_unit = fields.Boolean(string="¿Tiene unidad Secundaria?", related="product_id.is_secondary_unit",readonly=True)
    secondary_category_id = fields.Many2one(related="product_uom.category_id",string="Categoría Sec",readonly=True )

    @api.onchange('product_uom_qty', 'product_uom')
    def onchange_product_uom_qty(self):
        for rec in self:
            if rec and rec.is_secondary_unit == True and rec.sec_uom:
                rec.sec_qty = rec.product_uom._compute_quantity(rec.product_uom_qty, rec.sec_uom)
            else:
                rec.sec_qty = 0

    #@api.onchange('sec_qty', 'sec_uom')
    #def onchange_sec_qty(self):
    #    if self and self.is_secondary_unit == True and self.product_uom:
    #        self.product_uom_qty = self.sec_uom._compute_quantity(self.sec_qty, self.product_uom)
    #    else:
    #        self.product_uom_qty = 0

    @api.onchange('product_id')
    def onchange_secondary_uom(self):
        for rec in self:
            if rec.product_id.is_secondary_unit == True and rec.product_id.uom_id:
                rec.sec_uom = rec.product_id.secondary_uom.id
            elif rec.product_id.is_secondary_unit == False:
                rec.sec_uom = False
                rec.sec_qty = 0.0
    
    def _prepare_invoice_line(self, line=False,sequence=False):
        res = super(SaleOrderLine, self)._prepare_invoice_line(sequence=False)
        res.update({
            #'sec_qty':self.sec_qty,
            'sec_uom':self.sec_uom.id,
            })
        return res

    #@api.depends('product_uom_qty', 'product_uom','sec_uom')
    #def _compute_product_sec_uom_qty(self):
    #    for rec in self:
    #        rec.sec_qty = 0.0
    #        if rec.is_secondary_unit == True and rec.product_uom:
    #            rec.sec_qty = rec.product_uom._compute_quantity(rec.sec_qty, rec.sec_uom)