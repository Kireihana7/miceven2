# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Google Gmail",
<<<<<<< HEAD
    "version": "1.2",
=======
    "version": "1.0",
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    "category": "Hidden",
    "description": "Gmail support for incoming / outgoing mail servers",
    "depends": [
        "mail",
<<<<<<< HEAD
    ],
    "data": [
        "views/fetchmail_server_views.xml",
=======
        "google_account",
    ],
    "data": [
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        "views/ir_mail_server_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "auto_install": True,
<<<<<<< HEAD
    "license": "LGPL-3",
    "assets": {
        "web.assets_backend": [
            "google_gmail/static/src/scss/google_gmail.scss",
        ]
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
}
