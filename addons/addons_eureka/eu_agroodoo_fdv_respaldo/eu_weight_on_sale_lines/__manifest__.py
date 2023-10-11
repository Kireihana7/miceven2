# -*- coding: utf-8 Ñeri here!-*-
{
    'name': "Weight on sales lines",
    'version': '14.0.1.0',
    'category' : 'Stock',
    'license': 'Other proprietary',
    'summary': """Esta aplicación coloca el peso en las lineas de venta y el peso total de su orden""",
    'author': "CorpoEureka",
    'website': "http://www.corpoeureka.com",
    'description': """Peso en lineas de venta y compra
    """,
    'depends': [
                'base',
                'sale',
                'stock',
                'account',
                'purchase',
                'sale_stock',
                'sh_po_tender_management',
                #'add_product_purchase_order',
                ],
    'data':[
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/account_move_view.xml',
    ],
    'installable' : True,
    'application' : False,
}
