# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def write(self, vals):
        if vals.get("type") or vals.get("uom_id") or vals.get("tracking"): 
            for rec in self:
                existe_1 = True if len(self.env['purchase.order.line'].sudo().search([('product_id.product_tmpl_id','=',rec.id)],limit=1)) > 0 else False
                existe_2 = True if len(self.env['sale.order.line'].sudo().search([('product_id.product_tmpl_id','=',rec.id)],limit=1)) > 0 else False
                existe_3 = True if len(self.env['stock.move'].sudo().search([('product_id.product_tmpl_id','=',rec.id)],limit=1)) > 0 else False
                existe_4 = True if len(self.env['stock.move.line'].sudo().search([('product_id.product_tmpl_id','=',rec.id)],limit=1)) > 0 else False
                if existe_1 or existe_2 or existe_3 or existe_4:
                    raise UserError(('No puedes cambiar el tipo de Producto si tiene movimientos'))
        res = super(ProductTemplate, self).write(vals)
        return res