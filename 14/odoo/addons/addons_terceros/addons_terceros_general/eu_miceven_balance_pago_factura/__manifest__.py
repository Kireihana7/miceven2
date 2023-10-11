# -*- coding: utf-8 -*-
{   

    'name': 'Miceven Report Factura Pago',
    'version': '1.0',
    'author': 'CorpoEureka',
    'category': 'Ventas',
    'summary': '',
    'description': '''
        Reporte de Balance de Pagos por Factura
    ''',
    'depends': [
        'base',
        'account',
        'sale',
        'sale_management',
        'stock',
        'eu_weight_on_sale_lines',
        'eu_miceven_report_topper'

    ],
    'data': [
        'security/ir.model.access.csv',

        'views/account_report.xml',
        'views/report_invoice_payment.xml',
        'views/account_report.xml',
        'wizard/pago_miceven_wiz_views.xml',
        

    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}