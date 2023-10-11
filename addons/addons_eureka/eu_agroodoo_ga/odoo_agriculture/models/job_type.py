# -*- coding: utf-8 -*-

from odoo import api, fields, models, _  
from odoo.exceptions import UserError, ValidationError

class JobType(models.Model):
    _name = 'job.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'code'

    code = fields.Char(
        string='Code',
        required=True,
        default=lambda self: _('New'),
        tracking=True
    )

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True
    )

    type = fields.Selection(
        [
            ('material', 'Material'),
            ('labour', 'Labour'),
            ('equipment', 'Equipment'),
            ('overhead', 'Overhead'),
            ('hired_service', 'Hired Service')
        ],
        string='Type',
        required=True,
        tracking=True
    )    

    @api.model    
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            type = vals.get('type')
            prefix = ''
            
            if type == 'material':
                prefix = 'M'
            elif type == 'labour':
                prefix = 'L'
            elif type == 'equipment':
                prefix = 'E'
            elif type == 'overhead':
                prefix = 'O'
            elif type == 'hired_service':
                prefix = 'HS'                

            record_number = self.env['job.type'].search_count([('type', '=', type)])
            record_number += 1
            code = f'{prefix} - 00{record_number}'  
            vals['code'] = code or _('New')

        res = super(JobType, self).create(vals)        
        return res     