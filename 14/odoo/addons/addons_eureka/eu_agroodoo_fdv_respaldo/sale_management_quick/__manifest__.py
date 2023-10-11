# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quitar lo opcion de crear y editar en los campo many2one',
    'version':'1.0',
    'category': 'Sales/Sales',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'license' : 'OPL-1',
    'description': """
        .
        =============================================

        .
    """,
    'depends':[
    'sale_management',
    'mail',
    # 'crm',
    'todo_list',
    'stock',
    'delivery',
    ],

    'data':[
    'views/sale_form_views.xml'
    ],
    'installable': True,
    'application': True
}
