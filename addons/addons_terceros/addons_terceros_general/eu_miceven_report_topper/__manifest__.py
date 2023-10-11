# -*- coding: utf-8 -*-
{   

    'name': 'Miceven Report Header',
    'version': '1.0',
    'author': 'CorpoEureka',
    'category': 'Ventas',
    'summary': '',
    'description': '''
        Cabecera de Reportes de Miceven
    ''',
    'depends': [
        'base',
        'account',
        'sale',
        'sale_management',
        'stock',

    ],
    'data': [
        'views/account_report.xml',
        'views/header_report_invoice.xml',

    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}