# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Test API',
    'version': '1.0',
    'category': 'Hidden/Tests',
    'description': """A module to test the API.""",
    'depends': ['base', 'web', 'web_tour'],
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'security/test_new_api_security.xml',
        'views/test_new_api_views.xml',
        'data/test_new_api_data.xml',
    ],
<<<<<<< HEAD
    'assets': {
        'web.assets_tests': [
            # inside .
            'test_new_api/static/tests/tours/constraint.js',
            # inside .
            'test_new_api/static/tests/tours/x2many.js',
        ],
    },
=======
    'demo': [
    ],
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
