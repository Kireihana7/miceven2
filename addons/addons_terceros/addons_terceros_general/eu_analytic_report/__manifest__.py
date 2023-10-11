# -*- coding: utf-8 -*-
{
    'name': 'Analytic Report',
    'version': '14.0.0.1',
    'category': 'Account',
    'sequence': 35,
    'summary': 'Report por analytic moves',
    'depends': ['account',],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
