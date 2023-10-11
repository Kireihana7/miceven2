# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Online Event Ticketing",
    'category': 'Website/Website',
    'summary': "Sell event tickets online",
    'description': """
Sell event tickets through eCommerce app.
    """,
    'depends': ['website_event', 'event_sale', 'website_sale'],
    'data': [
        'data/event_data.xml',
        'report/event_sale_report_views.xml',
        'views/event_event_views.xml',
        'views/website_event_templates.xml',
        'views/website_sale_templates.xml',
        'security/website_event_sale_security.xml',
    ],
    'auto_install': True,
<<<<<<< HEAD
    'assets': {
        'web.assets_tests': [
            'website_event_sale/static/tests/**/*',
        ],
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
