# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountMove, self)._prepare_invoice_line_from_po_line(line)
        res.update({
            #'sec_qty':line.sec_qty,
            'sec_uom':line.sec_uom.id,
            })
        return res

    @api.model
    def create(self, vals):
        res= super(AccountMove, self).create(vals)
        for lines in res.invoice_line_ids:
            lines._compute_product_sec_uom_qty()
        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    sec_qty = fields.Float(string="Cantidad Sec.", digits=dp.get_precision('Product Unit of Measure'),readonly=True, compute="_compute_product_sec_uom_qty")
    sec_uom = fields.Many2one("uom.uom", string='UdM Secundaria', readonly=True)
    is_secondary_unit = fields.Boolean(related="product_id.is_secondary_unit", string="¿Tiene Unidad Secundaria?",readonly=True)
    secondary_category_id = fields.Many2one(related="product_uom_id.category_id",string="Categoría Sec",readonly=True)
    
    @api.onchange('quantity', 'product_uom_id')
    def onchange_product_uom_qty(self):
        if self and self.is_secondary_unit == True and self.sec_uom:
            self.sec_qty = self.product_uom_id._compute_quantity(self.quantity, self.sec_uom)

    #@api.onchange('sec_qty', 'sec_uom')
    #def onchange_sec_qty(self):
    #    if self and self.is_secondary_unit == True and self.product_uom_id:
    #        self.quantity = self.sec_uom._compute_quantity(self.sec_qty, self.product_uom_id)

    @api.onchange('product_id', 'product_uom_id')
    def onchange_secondary_uom(self):
        if self:
            for rec in self:
                if rec.product_id.is_secondary_unit == True and rec.product_id.uom_id:
                    rec.sec_uom = rec.product_id.secondary_uom.id
                elif rec.product_id.is_secondary_unit == False:
                    rec.sec_uom = False
                    rec.sec_qty = 0.0

    @api.depends('quantity', 'product_uom_id','sec_uom','is_secondary_unit')
    def _compute_product_sec_uom_qty(self):
        for rec in self:
            rec.sec_qty = 0.0
            if rec.is_secondary_unit and rec.sec_uom:
                rec.sec_qty = rec.product_uom_id._compute_quantity(rec.quantity, rec.sec_uom)
                #raise UserError(('%s')%(rec.sec_qty))
