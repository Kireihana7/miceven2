# -*- coding: utf-8 -*-
{
    'name': "Contactos, Ventas",
    'version': '1.0',
    'category' : 'Contacts - Contactos',
    'license': 'Other proprietary',
    'summary': """Esta aplicación permite visualizar otra moneda en la vista de Inventario.""",
    'author': "CorpoEureka",
    'license':'OPL-1',
    'website': "http://www.corpoeureka.com",
    'description': """
Esta APP añade campos en el módulo de contactos
    """,
    'depends': [
        'base',
        'contacts',
        'sale',
        'sale_management',
        'account',
        'municipality_tax',
        #'crm'
    ],
    'data':[
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        #'views/sales_order.xml',
        #'views/crm_view.xml',
        'views/account_move_view.xml',
        'views/inherid_plazo_pago.xml',
        'data/res_partner.xml',
    ],
    'installable' : True,
    'application' : False,
}