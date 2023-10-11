{
    'name': "TOTPortal",
    'category': 'Hidden',
    'depends': ['portal', 'auth_totp'],
    'auto_install': True,
    'data': [
        'security/security.xml',
        'views/templates.xml',
    ],
<<<<<<< HEAD
    'assets': {
        'web.assets_frontend': [
            'auth_totp_portal/static/src/**/*',
        ],
        'web.assets_tests': [
            'auth_totp_portal/static/tests/**/*',
        ],
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
