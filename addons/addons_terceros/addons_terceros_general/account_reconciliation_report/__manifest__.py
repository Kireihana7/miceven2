# -*- coding: utf-8 -*-
{
    'name': "Account Reconciled report ",

    'summary': """
       Account Reconciled Report for account module""",

    'description': """
        This app helps you to print the Account Reconciled Report .
    """,

    'author': "CorpoEureka",
    'website': "http://CorpoEureka.com/",
    'company': 'CorpoEureka',
    'category': 'Accounting',
    'version': '14.0.0.1',
    'depends': ['base',
     'account',
     'base',
     ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_views.xml',
    ],
    "application": True,
    "installable": True,
}
