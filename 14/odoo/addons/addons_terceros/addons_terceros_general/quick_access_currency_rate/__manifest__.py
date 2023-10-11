# -*- coding: utf-8 -*-
{
    'name': 'Odoo Currency Rate: Quick Access',
    'version': '13.0.1.0',
    'category': 'Accounting/Accounting',
    'description': """
    Quick access and update exchange rate daily
    """,
    'summary': '''
    Quick access and update exchange rate daily
    ''',
    'live_test_url': 'https://demo13.domiup.com',
    'author': 'Domiup',
    'price': 30,
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'domiup.contact@gmail.com',
    'website': 'https://www.youtube.com/watch?v=iJOnY4g0Sls&feature=youtu.be',
    'depends': [
        'account',
    ],
    'data': [
        'views/templates.xml',
        'security/ir.model.access.csv',
    ],

    'test': [],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'active': False,
    'application': True,
    'qweb': ['static/src/xml/*.xml'],
}
