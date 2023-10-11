# -*- coding: utf-8 -*-

{
    'name': 'Mass Mail Tests',
    'version': '1.0',
    'category': 'Hidden',
    'sequence': 8765,
    'summary': 'Mass Mail Tests: feature and performance tests for mass mailing',
    'description': """This module contains tests related to mass mailing. Those
are present in a separate module to use specific test models defined in
test_mail. """,
    'depends': [
        'mass_mailing',
        'mass_mailing_sms',
        'test_mail',
        'test_mail_sms',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
<<<<<<< HEAD
=======
    'application': False,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
