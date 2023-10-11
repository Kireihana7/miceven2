# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, modules,fields
from odoo.exceptions import UserError


class StockLocation(models.Model):
   _inherit= "stock.location"

   qty_max= fields.Float("Cantidad Max.")
   qty_occupied= fields.Float("Cantidad Ocup.",compute="_compute_qty_occupied")
   qty_per_occu= fields.Float("Porcentaje Ocupado", compute="_compute_qty_per_occu")
   capacity_type= fields.Many2one('uom.uom',"Unidad de medida")


   @api.constrains('qty_max','qty_occupied')
   def _constrain_qtys(self):
      for rec in self:
         if any([rec.qty_max<0,rec.qty_occupied<0]):
            raise UserError('No pueden usarse cantidades negativas')
   @api.depends('qty_max','qty_occupied')
   def _compute_qty_per_occu(self):
      for rec in self:
         if rec.qty_max>0:
            rec.qty_per_occu=100*(rec.qty_occupied/rec.qty_max)
         else:
            rec.qty_per_occu=0


   @api.depends('quant_ids','quant_ids.available_quantity','quant_ids.product_uom_id','capacity_type')
   def _compute_qty_occupied(self):
      for rec in self:
         quants=rec.quant_ids.filtered(lambda x: x.product_uom_id==rec.capacity_type)

         rec.qty_occupied=sum(quants.mapped('available_quantity'))
         