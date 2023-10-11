# -*- coding: utf-8 -*-
{
    'name': "eu_kaly_reportes",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','eu_multi_currency'],
    'data': [
        'security/ir.model.access.csv',

        # Reports
        'report/reporte_vendedores_ventas_report.xml',
        'report/reporte_vendedores_articulos_report.xml',

        # Wizard
        'wizard/kaly_reporte_views.xml',
        'wizard/reporte_vendedores_ventas_views.xml',
        'wizard/reporte_vendedores_articulos_views.xml',    
    ],
}
