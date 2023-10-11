# -*- coding: utf-8 -*-
# Copyright (c) Open Value All Rights Reserved

{
    'name': 'MRP Planning Engine MTO',
    'summary': 'MRP Planning Engine MTO',
    'version': '14.0.1.0',
    'category': 'Manufacturing',
    'website': 'www.openvalue.cloud',
    'author': "OpenValue",
    'support': 'info@openvalue.cloud',
    'license': "Other proprietary",
    'price': 500.00,
    'currency': 'EUR',
    'depends': [
        'sale_stock',
        'purchase_stock',
        'sale_purchase',
        'sale_mrp',
        'purchase_mrp',
        'mrp_product_costing',
        'mrp_planning_engine',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/stock_move_views.xml',
        'wizards/mrp_planning_engine_mto_views.xml',
        ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
