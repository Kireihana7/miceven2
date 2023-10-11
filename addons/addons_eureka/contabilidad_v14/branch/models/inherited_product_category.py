# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductCategoryIn(models.Model):
    _inherit = 'product.category'

    
    # @api.model
    # def default_get(self, default_fields):
    #     res = super(ProductCategoryIn, self).default_get(default_fields)
    #     if self.env.user.branch_id:
    #         res.update({
    #             'branch_id' : self.env.user.branch_id.id or False
    #         })
    #     return res
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        tracking=True,
        invisible=True,
    )
    branch_id = fields.Many2one('res.branch', string="Branch")