# -*- coding: utf-8 -*-
# Copyright (c) OpenValue All Rights Reserved

{
  'name': 'MRP Planning Engine Enhancement',
  'summary': 'MRP Planning Engine',
  'version': '15.0.2.1',
  'category': 'Manufacturing',
  "website": 'www.openvalue.cloud',
  'author': "OpenValue",
  'support': 'info@openvalue.cloud',
  'license': 'Other proprietary',
  'price': 0.00,
  'currency': 'EUR',
  'depends': [
        "mrp_planning_engine",
        "web_widget_x2many_2d_matrix",
        "date_range",
    ],
    'data': [
        "security/stock_reorder_point_security.xml",
        "security/ir.model.access.csv",
        "views/product_product_views.xml",
        "views/stock_orderpoint_views.xml",
        "wizards/mrp_demand_create_tool_views.xml",
        "views/mrp_date_range_menus.xml",
    ],
  'application': False,
  'installable': True,
  'auto_install': False,
  'images': ['static/description/banner.png'],
}
