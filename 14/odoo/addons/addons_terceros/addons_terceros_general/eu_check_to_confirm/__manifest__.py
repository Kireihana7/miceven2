# -*- coding: utf-8 -*-
{
    'name': "Button Confirm Global",
    'version': '14.0.1.0',
    'category' : 'Stock',
    'license': 'Other proprietary',
    'summary': """Esta aplicación Múltiples permisos para la confirmación de los Documentos""",
    'author': "CorpoEureka",
    'website': "http://www.corpoeureka.com",
    'description': """
    """,
    'depends': [
                'stock',
                'base',
                'account',
                'purchase',
                'sale',
                ],
    'data':[
        'security/security.xml',
        'views/views.xml',
    ],
    'installable' : True,
    'application' : False,
}
