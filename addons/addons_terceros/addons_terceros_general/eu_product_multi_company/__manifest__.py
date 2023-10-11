# -*- coding: utf-8 -*-
{
    'name': 'Regla Multi Company Product',
    'version': '14.0.1.1',
    'category': 'Product',
    'sequence': 35,
    'summary': 'Productos que la regla sea multi compañía en productos',
    'depends': [
        'stock',
        'product',
        'base'
    ],
    'data': [
        'security/multi_company.xml',
        'view/product_view.xml',
    ],
    'installable': True,
}
