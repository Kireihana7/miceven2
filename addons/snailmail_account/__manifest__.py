# -*- coding: utf-8 -*-
{
    'name': "snailmail_account",
    'description': """
Allows users to send invoices by post
=====================================================
        """,
    'category': 'Hidden/Tools',
    'version': '0.1',
    'depends': ['account', 'snailmail'],
    'data': [
        'views/res_config_settings_views.xml',
        'wizard/account_invoice_send_views.xml',
        'security/ir.model.access.csv',
    ],
    'auto_install': True,
<<<<<<< HEAD
    'assets': {
        'web.assets_backend': [
            'snailmail_account/static/**/*',
        ],
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
