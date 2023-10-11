# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class EosDownloadTask(models.Model):
    _name = 'eos.download.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        readonly=True,
        default=lambda self: _('New')
    )

    @api.model    
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('eos.download.task') or _('New')        
        res = super(EosDownloadTask, self).create(vals)
        return res    