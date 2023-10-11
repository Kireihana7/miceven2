# -*- coding: utf-8 -*-
{
    'name': "Sale Dashboard Map",

    'summary': """
        Geographical representation with hot zones for sales analysis""",

    'description': """
        Geographical representation with hot zones for sales analysis
    """,
    'author': 'José Luis Vizcaya López',
    'company': 'José Luis Vizcaya López',
    'maintainer': 'José Luis Vizcaya López',
    'live_test_url':'https://youtu.be/ZcyB2HgjJ5U',
    'website': 'https://github.com/birkot',
    'category': 'Sales',
    "version": "14.0.1.0.0",
    "application": False,
    'depends': ['base', 'sale'],
    'data': [
        'views/res_country.xml',
        'views/sale_dashboard_map.xml',
    ],
    'qweb': ["static/src/xml/sale_dashboard_template.xml"],
    'post_init_hook': 'sale_dashboard_map_prepared',
    "license": "OPL-1",
    'images': [
        'static/description/thumbnail.png',
    ],
    "price": 20,
    "currency": "USD",
    "auto_install": False,
    "installable": True,
}
