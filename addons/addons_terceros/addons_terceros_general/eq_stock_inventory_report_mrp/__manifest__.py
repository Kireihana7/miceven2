# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

{
    'name': "Stock Inventory Report Manufacturing",
    'category': 'Stock',
    'version': '14.0.1.2',
    'author': 'Equick ERP',
    'description': """
        This Module allows you to generate Stock Inventory Report PDF/XLS wise.
        * Allows you to Generate Stock Inventory PDF/XLS Report.
        * Support Multi Warehouse And Multi Locations.
        * Group By Product Category Wise.
        * Filter By Product/Category Wise.
    """,
    'summary': """ This Module allows you to generate Inventory Report.Inventory Report | stock mrp Report | Real Time mrp Report | Real Time manufacturing Report | Stock card | Inventory Report | Odoo Inventory mrp Report | location wise report.""",
    'depends': ['base', 'mrp'],
    'price': 45,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_stock_inventory_view.xml',
        'report/report.xml',
        'report/stock_inventory_template_report.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: