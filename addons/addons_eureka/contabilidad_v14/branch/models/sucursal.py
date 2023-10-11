# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ImplementSucursal(models.Model):
    _inherit = 'implement.sucursal'

    
    @api.model
    def default_get(self, default_fields):
        res = super(ImplementSucursal, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id' : self.env.user.branch_id.id or False
            })
        return res

    sucursal_id = fields.Many2one('res.branch', string="Sucursal", options='{"no_open": True, "no_create_edit": True, "no_quick_create": True, "no_create": True}')