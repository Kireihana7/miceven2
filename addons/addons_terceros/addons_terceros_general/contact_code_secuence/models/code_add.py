# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class ContactSequence(models.Model):
    _inherit = 'res.partner'
    

    code = fields.Char(string="Customer code", readonly=True)
    
    @api.model    
    def create(self, vals):
        code = self.env['ir.sequence'].next_by_code('contact.code.seq')
        vals.update({
            'code': code
            })
        res = super(ContactSequence, self).create(vals)
        return res  

    # def write(self,vals):
    #     for rec in self:
    #         if not rec.code:
    #             code = self.env['ir.sequence'].next_by_code('contact.code.seq')
    #             vals.update({
    #                 'code': code
    #                 })

    #     res = super(ContactSequence, self).write(vals)
    #     return res  
