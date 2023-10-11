# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

<<<<<<< HEAD
from odoo import api, fields, models
=======
from odoo import fields, models
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe


class TestModel(models.Model):
    """ Add website option in server actions. """

    _name = 'test.model'
<<<<<<< HEAD
    _inherit = [
        'website.seo.metadata',
        'website.published.mixin',
        'website.searchable.mixin',
    ]
    _description = 'Website Model Test'

    name = fields.Char(required=1)

    @api.model
    def _search_get_detail(self, website, order, options):
        return {
            'model': 'test.model',
            'base_domain': [],
            'search_fields': ['name'],
            'fetch_fields': ['name'],
            'mapping': {
                'name': {'name': 'name', 'type': 'text', 'match': True},
                'website_url': {'name': 'name', 'type': 'text', 'truncate': False},
            },
            'icon': 'fa-check-square-o',
            'order': 'name asc, id desc',
        }
=======
    _inherit = ['website.seo.metadata', 'website.published.mixin']
    _description = 'Website Model Test'

    name = fields.Char(required=1)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
