# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class EosField(models.Model):
    _name = 'eos.field'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        readonly=True,
        default=lambda self: _('New')
    )

    @api.model    
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('eos.field') or _('New')        
        res = super(EosField, self).create(vals)
        return res    

class EosFieldClassificationArea(models.Model):
    _name = 'eos.field.classification.area'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        readonly=True,
        default=lambda self: _('New')
    )

    eos_field_id = fields.Many2one('eos.field', string='EOS Field', required=True)

    @api.model    
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('eos.field.classification.area') or _('New')        
        res = super(EosFieldClassificationArea, self).create(vals)
        return res            