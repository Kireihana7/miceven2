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


class ResCompany(models.Model):
    _inherit = 'res.company'

    product_inventory_status = fields.Boolean(string='Send Product Inventory Status',readonly=False)
    filter_by = fields.Selection([('product','Product'),('category','Category')], string='Filter By')
    user_id = fields.Many2many('res.users', string='Users')
    product_id = fields.Many2one('product.template', string='Product')
    category_id = fields.Many2one('product.category', string='Category')
    send_by = fields.Selection([('minutes','Minutes'),('hours','Hours'),('days','Days'),('weeks','Weeks'),('months','Months')], string='Filter By')
    execute_every = fields.Integer(string='Execute Every')
    order_by = fields.Selection([('ascending','Qty Ascending'),('descending','Qty Descending')], default='ascending', string='Order By')
    

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_inventory_status = fields.Boolean(related='company_id.product_inventory_status', string='Send Product Inventory Status',readonly=False)
    user_id = fields.Many2many(related='company_id.user_id', string='User',readonly=False)
    filter_by = fields.Selection(related='company_id.filter_by', string='Filter By',readonly=False)
    product_id = fields.Many2one(related='company_id.product_id', string='Product',readonly=False)
    category_id = fields.Many2one(related='company_id.category_id', string='Category',readonly=False)
    send_by = fields.Selection(related='company_id.send_by', string='Send By',readonly=False)
    execute_every = fields.Integer(related='company_id.execute_every', string='Execute Every',readonly=False)
    order_by = fields.Selection(related='company_id.order_by', string='Order By', readonly=False)
    
    
    
    
    @api.onchange('send_by','execute_every')
    def cron_send_by(self):
        if self.send_by:
            cron_id = self.env['ir.cron'].search([('cron_name','=','Product Inventory Status')])
            if self.send_by:
                if self.execute_every:
                    cron_id.write({'interval_number' :self.execute_every})
            if self.send_by == 'minutes':
                cron_id.write({'interval_type' :'minutes'})
            elif self.send_by == 'hours':
                cron_id.write({'interval_type' :'hours'})
            elif self.send_by == 'days':
                cron_id.write({'interval_type' :'days'})
            elif self.send_by == 'weeks':
                cron_id.write({'interval_type' :'weeks'})
            elif self.send_by == 'months':
                cron_id.write({'interval_type' :'months'})
            
            
                
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
