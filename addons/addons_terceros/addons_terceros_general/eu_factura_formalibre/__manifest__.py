# -*- coding: utf-8 -*-
{   

    'name': 'Factura Forma Libre (Kaly)',
    'version': '1.0',
    'author': 'CorpoEureka',
    'category': 'Ventas',
    'summary': '',
    'description': '''
        Factura Forma Libre
    ''',
    'depends': [
        'base',
        'account',
        'sale',
        'sale_management',
        'stock',
        'eu_add_field_partner',
        'eu_agroindustry',
    ],
    'data': [
        'views/report_invoice.xml',
        'views/report_invoice_with_iva.xml',
        'views/account_view.xml',
        'views/report_so.xml',
        'views/report_albaran.xml',
        'views/account_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}