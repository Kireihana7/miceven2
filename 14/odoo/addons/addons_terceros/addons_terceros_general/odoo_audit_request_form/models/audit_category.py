# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import fields, api, models, _


class CustomAuditCategory(models.Model):
    _name = "custom.audit.category"
    _description = 'Audit Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name', 
        copy=False,
        required=True,
        tracking=True
    )
    code = fields.Char(
        string='Code', 
        copy=False,
        required=True,
        tracking=True
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: