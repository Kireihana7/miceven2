# -*- coding: utf-8 -*-
{
    'name': "User Login/Logout Status",

    'summary': """""",

    'description': """
        User Login/Logout Status and User total Login Time Status viewer
    """,

    'author': "Md. Hossain Akash",
    'website': "https://mdakash.xyz",
    'category': 'Administration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/setting.xml',
    ],
    'license': 'AGPL-3',
    # 'price': 5.0,
    # 'currency': 'USD'
}
