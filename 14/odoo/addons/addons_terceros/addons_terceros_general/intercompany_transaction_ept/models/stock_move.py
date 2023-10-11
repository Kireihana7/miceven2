"""
For inter_company_transfer_ept module.
"""
from odoo import models,fields,api
from odoo.exceptions import UserError

class StockMove(models.Model):
    """
    Inherited for passing values to picking.
    @author: Maulik Barad on Date 16-Oct-2019.
    """
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """
        Inherited for adding relation with ICT if created by it.
        @author: Maulik Barad on Date 16-Oct-2019.
        @return: Dictionary for creating picking.
        """
        vals = super(StockMove, self)._get_new_picking_values()
        if self.sale_line_id.order_id.inter_company_transfer_id:
            vals.update({
                'inter_company_transfer_id':self.sale_line_id.order_id.inter_company_transfer_id.id
                })
        return vals

    intertransf=fields.Many2one('inter.company.transfer.ept',related="picking_id.inter_company_transfer_id")

    def _account_entry_move(self, qty, description, svl_id, cost):
        if self.picking_id.inter_company_transfer_id and self.picking_id.inter_company_transfer_id.type == 'internal':
            return True
        return super(StockMove,self)._account_entry_move(qty, description, svl_id, cost)


class StockLocation(models.Model):
    
    _inherit="stock.location"
    
    check_always_False=fields.Boolean("check_false")

class Stockwarehouse(models.Model):
    
    _inherit="stock.warehouse"
    
    check_always_False=fields.Boolean("check_false")


class StockPickingType(models.Model):
    
    _inherit="stock.picking.type"
    
    check_always_False=fields.Boolean("check_false",readonly=True)



class StockMoveLine(models.Model):
    
    _inherit="stock.move.line"
    

    intertransf=fields.Many2one('inter.company.transfer.ept',related="move_id.intertransf")
    # @api.model
    # @api.onchange('intertransf')
    # def onchange_intertransf(self):
    #     # res = super().default_get(default_fields)
    #     lot_id=False
    #     # if self._context.get('active_model')=="stock.picking" :
    #     #     intertransf=self.env["stock.picking"].search([('id','=',self._context.get('active_id'))]).inter_company_transfer_id
    #     # elif self._context.get('active_model')=="inter.company.transfer.ept" :
    #     #     intertransf=self.env["inter.company.transfer.ept"].search([('id','=',self._context.get('active_id'))])
    #     # else:
    #     #     intertransf=False

    #     if self.intertransf:
    #         the_other_picking=self.intertransf.picking_ids.filtered(lambda x:x.picking_type_id.code!="incoming")


    #         if the_other_picking: #.state=="done":
    #             lines=the_other_picking.move_line_ids_without_package.filtered(lambda x: x.product_id==self.product_id)
    #             if lines:
    #                 self.lot_id=lines[0].lot_id
                    
    #     # return res 
