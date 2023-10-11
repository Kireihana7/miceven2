# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Web Expand Print Report In Odoo",
    'summary': """This module helps to print Pdf and Excel Reports for List View & Filter with any group and you will get button to expand or collapse in a single click.""",
    'description': """This module helps to print Pdf and Excel Reports for List View & Filter with any group and you will get button to expand or collapse in a single click.""",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'category': 'Extra Toos',
    'version': '14.0.0.1',
    'depends': ['web'],
    'data': [
        'data/list_data.xml',
        'views/list_report_document.xml',
        'views/assets.xml',
    ],
    'qweb' : [
        'static/src/xml/expand_buttons.xml',
    ],
    'installable': True,
    'images' : ['static/description/banner.png'],
    'price':14.99,
    'live_test_url': 'https://youtu.be/g0pYjhgMKKk',
    'currency': 'USD',
    'auto_install': False,
    'application': False
}
