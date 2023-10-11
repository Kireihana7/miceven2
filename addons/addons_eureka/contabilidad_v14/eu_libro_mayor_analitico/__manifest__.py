# -*- coding: utf-8 -*-
{
    'name': "eu_libro_mayor_analitico",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'account', 'eu_multi_currency'],
    'data': [
        'security/ir.model.access.csv',
        'report/libro_mayor_analitico_report.xml',
        'report/libro_mayor_analitico_actions.xml',
        'wizard/libro_mayor_analitico_views.xml',
    ],
}
