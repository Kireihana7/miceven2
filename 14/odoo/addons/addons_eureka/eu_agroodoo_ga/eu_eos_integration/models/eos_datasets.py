# -*- coding: utf-8 -*-

import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class EosDatasets(models.Model):
    _name = 'eos.datasets'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        readonly=True,
        default=lambda self: _('New')
    )

    default_dataset_id = fields.Char(
        string='dataset_id',
    )    

    availability_by_date = fields.Char(
        string='Available images by dates',
    )    

    abbreviation_ids = fields.Many2many('eos.datasets.abbreviation', 'datasets_abb_rel', 'dataset_id', 'dataset_abbreviation_id')