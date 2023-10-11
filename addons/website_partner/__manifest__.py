# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Partner',
    'category': 'Hidden',
    'summary': 'Partner module for website',
    'version': '0.1',
    'description': """
This is a base module. It holds website-related stuff for Contact model (res.partner).
    """,
    'depends': ['website'],
    'data': [
        'views/res_partner_views.xml',
        'views/website_partner_templates.xml',
        'data/website_partner_data.xml',
    ],
    'demo': ['data/website_partner_demo.xml'],
    'installable': True,
<<<<<<< HEAD
=======
    'auto_install': False,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
