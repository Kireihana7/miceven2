# -*- coding: utf-8 -*-
{
    "name": "Eureka commissions Total",
    "version": "14.0.1.2.0",
    "author": "CorpoEureka",
    "category": "Sales",
    "license": "OPL-1",
    "depends": [
        "account", 
        "product", 
        "sale_management",
        "contacts",
    ],
    "data": [
        "data/sequence.xml",
        "security/ir.model.access.csv",
        "security/sale_commission_security.xml",
        "views/sale_commission_view.xml",
        "views/sale_commission_full_view.xml",
        "views/sale_commission_line_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
        "views/account_move_views.xml",
        "wizard/sale_commission_payment_view.xml",
    ],
    "installable": True,
}
