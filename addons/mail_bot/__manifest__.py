# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'OdooBot',
    'version': '1.2',
    'category': 'Productivity/Discuss',
    'summary': 'Add OdooBot in discussions',
    'website': 'https://www.odoo.com/app/discuss',
    'depends': ['mail'],
    'auto_install': True,
    'installable': True,
    'data': [
        'views/res_users_views.xml',
        'data/mailbot_data.xml',
    ],
    'demo': [
        'data/mailbot_demo.xml',
    ],
<<<<<<< HEAD
    'assets': {
        'web.assets_backend': [
            'mail_bot/static/src/scss/odoobot_style.scss',
        ],
    },
=======
    'qweb': [
        'static/src/bugfix/bugfix.xml',
    ],
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
