# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Indian - Point of Sale',
    'icon': '/l10n_in/static/description/icon.png',
    'version': '1.0',
    'description': """GST Point of Sale""",
    'category': 'Accounting/Localizations/Point of Sale',
    'depends': [
        'l10n_in',
        'point_of_sale'
    ],
    'demo': [
        'data/product_demo.xml',
    ],
    'auto_install': True,
<<<<<<< HEAD
    'assets': {
        'point_of_sale.assets': [
            'l10n_in_pos/static/src/js/**/*',
            'l10n_in_pos/static/src/xml/**/*',
        ],
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
