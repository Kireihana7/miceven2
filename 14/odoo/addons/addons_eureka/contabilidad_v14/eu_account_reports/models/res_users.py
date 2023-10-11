# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    is_vendor = fields.Boolean(string='Es vendedor', default=False)