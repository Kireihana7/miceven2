# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.

from odoo import models, fields

class CustomAuditRefuseWizard(models.TransientModel):
    _name = 'custom.audit.refuse.wizard'
    _description = 'Audit Refuse Wizard'

    refuse_reason = fields.Text(
        string='Refuse Reason', 
        copy=False,
        required=True
    )
   
    def custom_action_refuse(self):
        audit_request_id = self.env['custom.audit.request'].browse(self._context.get('active_ids'))
        audit_request_id.state = 'f_refuse'
        audit_request_id.refuse_reason = self.refuse_reason
        audit_request_id.refuse_user_id = self.env.user.id
        audit_request_id.date_refuse = fields.Date.today()
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: