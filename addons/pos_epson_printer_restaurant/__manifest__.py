# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'pos_epson_printer_restaurant',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Epson Printers as Order Printers',
    'description': """

Use Epson Printers as Order Printers in the Point of Sale without the IoT Box
""",
    'depends': ['pos_epson_printer', 'pos_restaurant'],
    'data': [
        'views/pos_restaurant_views.xml',
    ],
    'installable': True,
    'auto_install': True,
<<<<<<< HEAD
    'assets': {
        'point_of_sale.assets': [
            'pos_epson_printer_restaurant/static/**/*',
        ],
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
