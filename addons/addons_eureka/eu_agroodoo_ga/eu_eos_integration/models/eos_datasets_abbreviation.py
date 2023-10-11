# -*- coding: utf-8 -*-

import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class EosDatasetsAbbreviation(models.Model):
    _name = 'eos.datasets.abbreviation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        readonly=True,
    )