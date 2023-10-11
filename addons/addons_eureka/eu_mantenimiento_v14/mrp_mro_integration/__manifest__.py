# -*- coding: utf-8 -*-
# Copyright (c) Open Value All Rights Reserved

{
    'name': 'MRP MRO Maintenance Integration',
    'summary': 'MRP MRO Maintenance Integration',
    'version': '14.0.1.0',
    'category': 'Manufacturing',
    'website': 'www.openvalue.cloud',
    'author': "OpenValue",
    'support': 'info@openvalue.cloud',
    'license': "Other proprietary",
    'price': 1000.00,
    'currency': 'EUR',
    'depends': [
        'mrp_shop_floor_control',
        'mro_maintenance',
        ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/mro_request_production_wizard_views.xml',
        'wizards/mro_request_workcenter_wizard_views.xml',
        'views/mrp_workcenter_views.xml',
        'views/mrp_production_views.xml',
        'views/mrp_workorder_views.xml',
        ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
