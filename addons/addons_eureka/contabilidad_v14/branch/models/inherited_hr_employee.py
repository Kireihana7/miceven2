# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

class Hremployee(models.Model):
    _inherit = 'hr.employee'
    
    
    @api.model
    def default_get(self, default_fields):
        res = super(Hremployee, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id' : self.env.user.branch_id.id or False
            })
        return res

    branch_id = fields.Many2one('res.branch', string="Sucursal")


class HremployeeP(models.Model):
    _inherit = 'hr.employee.public'
    
    

    branch_id = fields.Many2one('res.branch', string="Sucursal")