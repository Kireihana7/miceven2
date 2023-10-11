# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SeedVariety(models.Model):
    _name = 'seed.variety'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def default_get(self, fields):
        res = super(SeedVariety, self).default_get(fields)
        res['crop_id'] = self.env.context.get('default_crop_id')
        return res    

    name = fields.Char(
        string='Name',
        required=True,
    )

    seed_type_id = fields.Many2one('seed.type', required=True, string='Seed Type')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
