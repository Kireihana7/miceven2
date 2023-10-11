# -*- coding: utf-8 -*-

{
    'name': 'Product Extra Security ',
    'version':'14.0',
    'category': 'Stock',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'license' : 'OPL-1',
    'description': """

    """,
    'depends':[
    	'base',
    	'account',
    	'stock',
    	'product',
    ],
    'data':[
        'security/security.xml',
        'views/product_view.xml',
    ],
    'images': ['static/description/eureka_banner.png'],
    'installable': True,
    'application': True
}
