# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'No crear y Editar en Inventario',
    'version':'1.0',
    'category': 'Stock',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'license' : 'OPL-1',
    'description': """
        .

        Quitar lo opcion de crear y editar en los campo many2one
        =============================================

        .
    """,
    'depends':[
    'stock',
    'stock_picking_batch',
    'product',
    'uom',
    'purchase',
    'purchase_stock',
    'purchase_requisition',
    'account',
    'sale_management',
    ],

    'data':[
    'views/stock_form_views.xml'
    ],
    'installable': True,
    'application': True
}
