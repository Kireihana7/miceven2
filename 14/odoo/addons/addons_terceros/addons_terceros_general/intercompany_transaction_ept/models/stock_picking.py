"""
For inter_company_transfer_ept module.
"""
from odoo import fields, api, models


class Picking(models.Model):
    """
    Inherited for adding relation with inter company transfer.
    @author: Maulik Barad on Date 25-Sep-2019.
    """
    _inherit = 'stock.picking'

    inter_company_transfer_id = fields.Many2one('inter.company.transfer.ept', string="ICT",
                                                copy=False, help="Reference of ICT.")

    inter_company_transfer_id_new = fields.Many2one('inter.company.transfer.ept', string="ICT",
                                                copy=False, help="Referencia del ICT.")

    def _create_backorder(self):
        """
        Inherited for adding ICT relation to backorder also.
        @author: Maulik Barad on Date 09-Oct-2019.
        """
        res = super(Picking, self)._create_backorder()
        for backorder in res:
            if backorder.backorder_id and backorder.backorder_id.inter_company_transfer_id:
                backorder.write({"inter_company_transfer_id":backorder.backorder_id.\
                                 inter_company_transfer_id.id})
            if backorder.backorder_id and backorder.backorder_id.inter_company_transfer_id_new:
                backorder.write({"inter_company_transfer_id_new":backorder.backorder_id.\
                                 inter_company_transfer_id_new.id})
        return res

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        # Prevent copy of the carrier and carrier price when generating return picking
        # (we have no integration of returns for now)
        new_picking, pick_type_id = super(StockReturnPicking, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'inter_company_transfer_id': self.picking_id.inter_company_transfer_id.id or False})
        return new_picking, pick_type_id