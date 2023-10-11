# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Restaurant Adyen',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'Adds American style tipping to Adyen',
    'depends': ['pos_adyen', 'pos_restaurant', 'payment_adyen'],
    'data': [
        'views/pos_payment_method_views.xml',
<<<<<<< HEAD
        ],
    'auto_install': True,
    'assets': {
        'point_of_sale.assets': [
            'pos_restaurant_adyen/static/**/*',
        ],
    },
=======
        'views/point_of_sale_assets.xml',
    ],
    'auto_install': True,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
