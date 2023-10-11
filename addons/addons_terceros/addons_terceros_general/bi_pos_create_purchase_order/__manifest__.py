# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Purchase Order- Create Purchase Order from POS in Odoo",
    "version" : "14.0.0.0",
    "category" : "Point of Sale",
    'summary': 'Create Purchase from Point of Sale create purchase from pos create purchase order from point of sale Create purchase from POS Generate purchase order from POS create SO from POS convert purchase from pos create purchase from pos purchase order create sale',
    "description": """
    
                 This odoo app helps user to create purchase order directly from point of sale order screen, user can configure purchase order state, Purchase order will created with customer and product from point of sale order with same quantity in configured state. User can view purchase order from pos session, filter and group by purchase order created from point of sale. 
    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 15,
    "currency": 'EUR',
    "depends" : ['base','point_of_sale','purchase'],
    "data": [
        "views/bipos_config_inherit.xml",
        "views/custom_pos_view.xml",
    ],
    'qweb': [
        'static/src/xml/pos_create_purchase_order.xml',
    ],
    "auto_install": False,
    "installable": True,
	"live_test_url":'https://youtu.be/SF6fZUZppsk',
	"images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
