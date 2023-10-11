# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class product_template(models.Model):
    _inherit = 'product.template'
    
    def_company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    
    def cron_inventory_status(self):
        #print ("cal===============")
        user_ids = self.env.user.company_id.user_id
        template_id = self.env['ir.model.data'].get_object_reference('dev_product_inventory_status', 'email_template_inventory')[1]
        for user_id in user_ids:
            mtp = self.env['mail.template'].browse(template_id)
            mtp.write({'email_to': 'jmazzei@corporacioneureka.com'})
            mtp.send_mail(26,force_send=True)
        #return True



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
