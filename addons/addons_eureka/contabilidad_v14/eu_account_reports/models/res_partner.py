# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

class Partner(models.Model):
    _inherit = 'res.partner'

    is_vendor = fields.Boolean(string='Es vendedor', compute='_compute_is_vendor', store=True)

    @api.depends('user_id.is_vendor')
    def _compute_is_vendor(self):
        for rec in self:
            rec.is_vendor = rec.user_id.is_vendor