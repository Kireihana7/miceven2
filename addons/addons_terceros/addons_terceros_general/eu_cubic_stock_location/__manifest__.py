# -*- coding: utf-8 -*-
# Autor: José D.Ñeri
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Eu Cap. Ub. Inv.',
    'category': 'Stock',
    'sequence': 150,
    'author' : 'Corporación Eureka',
    'summary': 'Capacity in Stock.Location',
    'description': """
Este módulo agrega campos para capacidad en las ubicaciones de inventario 
""",
    'depends': [
        'base', 
        'stock'],
    'data': [
        # 'security/security.xml', 
        'security/ir.model.access.csv',
        'views/menu_view_model.xml',
    ],
    'installable': True,
}
