# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{   

    'name': 'Campo de descuento en el modulo de ventas',
    'version': '1.0',
    'author': 'CorpoEureka',
    'category': 'Ventas',
    'summary': 'Descuento total en ventas',
    'description': '''
        Este modulo agrega un campo de descuento:
            En este campo se muentra el total de descuento en los pedidos de venta

    ''',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}