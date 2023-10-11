# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning,UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    warehouse_id = fields.Many2one(
        'stock.warehouse',
       domain="[('company_id', '=', company_id),'|',('branch_id','=',branch_id),('branch_id','=',False)]",default=False
       )
    branch_id = fields.Many2one('res.branch', string="Branch")
    @api.model
    def default_get(self,fields):
        res = super(SaleOrder, self).default_get(fields)
        branch_id = warehouse_id = False
        if self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        if branch_id:
            branched_warehouse = self.env['stock.warehouse'].search([('branch_id','=',branch_id)])
            if branched_warehouse:
                warehouse_id = branched_warehouse.ids[0]
            else:
                warehouse_id=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id),('branch_id','=',False)], limit=1).id
        else:
            warehouse_id=self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id),('branch_id','=',False)], limit=1)

            warehouse_id = warehouse_id.id

        res.update({
            'branch_id' : branch_id,
            'warehouse_id' : warehouse_id
            })

        return res

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id_cycle(self):
        for rec in self:
            if rec.warehouse_id and (rec.warehouse_id.company_id!=self.env.company or rec.warehouse_id.branch_id not in [rec.branch_id,False]):
                warehouse_id=False
                if self.env.user.branch_id:
                    branch_id = self.env.user.branch_id.id
                    if branch_id:
                        branched_warehouse = self.env['stock.warehouse'].search([('branch_id','=',branch_id)])
                    if branched_warehouse:
                        warehouse_id = branched_warehouse[0]
                    else:
                        warehouse_id=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id),('branch_id','=',False)], limit=1)
                else:
                    warehouse_id=self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id),('branch_id','=',False)], limit=1)

                    warehouse_id = warehouse_id
                rec.warehouse_id=warehouse_id
    
    
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['branch_id'] = self.branch_id.id
        return res


    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise Warning("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.")