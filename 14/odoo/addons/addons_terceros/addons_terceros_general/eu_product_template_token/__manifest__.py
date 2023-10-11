# -*- coding: utf-8 -*- Ñeri here

{
    'name': 'Ficha de producto alpha',
    'category': 'Misc',
    'sequence': 150,
    'summary': '',
    'author': 'CorpoEureka',
    'license':'OPL-1',
    'description': """
un nuevo repórte en productos (template)!
""",
    'depends': [
        'base', 
        'stock',
        'add_product_purchase_order',
        'product',
        'purchase',
    ],
    'data': [
        'report/product_template_token.xml',
        'report/product_minum_stock_report.xml',
        'report/label.xml',
        'report/report_actions.xml',
        'views/min_stock_wiz_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
