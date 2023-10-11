# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    branch_id = fields.Many2one('res.branch')

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise Warning("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.") 


    @api.model
    def create(self, vals):
        res=super().create(vals)
        for rec in res:
            if rec.view_location_id:
                rec.view_location_id.branch_id=rec.branch_id
            if rec.wh_input_stock_loc_id:
                rec.wh_input_stock_loc_id.branch_id=rec.branch_id
            if rec.wh_qc_stock_loc_id:
                rec.wh_qc_stock_loc_id.branch_id=rec.branch_id
            if rec.wh_output_stock_loc_id:
                rec.wh_output_stock_loc_id.branch_id=rec.branch_id
            if rec.wh_pack_stock_loc_id:
                rec.wh_pack_stock_loc_id.branch_id=rec.branch_id
            if rec.pbm_loc_id:
                rec.pbm_loc_id.branch_id=rec.branch_id
            if rec.sam_loc_id:
                rec.sam_loc_id.branch_id=rec.branch_id
            if rec.lot_stock_id:
                rec.lot_stock_id.branch_id=rec.branch_id
        return res
class StockPickingTypeIn(models.Model):
    _inherit = 'stock.picking.type'

    branch_id = fields.Many2one('res.branch',related='warehouse_id.branch_id', store=True,)
