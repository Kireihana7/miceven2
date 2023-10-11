# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
<<<<<<< HEAD
    'name': 'Saudi Arabia - Point of Sale',
=======
    'name': 'K.S.A. - Point of Sale',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'author': 'Odoo S.A',
    'category': 'Accounting/Localizations/Point of Sale',
    'description': """
K.S.A. POS Localization
=======================================================
    """,
    'license': 'LGPL-3',
<<<<<<< HEAD
    'depends': [
        'l10n_gcc_pos',
        'l10n_sa',
    ],
    'assets': {
        'point_of_sale.assets': [
            'web/static/lib/zxing-library/zxing-library.js',
            'l10n_sa_pos/static/src/js/models.js',
            'l10n_sa_pos/static/src/xml/OrderReceipt.xml',
        ]
    },
=======
    'depends': ['l10n_gcc_pos', 'l10n_sa_invoice'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
    ],
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'auto_install': True,
}
