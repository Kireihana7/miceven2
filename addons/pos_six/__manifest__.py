# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Six',
    'version': '1.0',
    'category': 'Sales/Point Of Sale',
    'sequence': 6,
    'summary': 'Integrate your POS with a Six payment terminal',
    'data': [
        'views/pos_payment_method_views.xml',
    ],
    'qweb': [
        'static/src/xml/BalanceButton.xml',
        'static/src/xml/Chrome.xml',
    ],
    'depends': ['point_of_sale'],
    'installable': True,
    'license': 'LGPL-3',
<<<<<<< HEAD
    'assets': {
        'point_of_sale.assets': [
            'pos_six/static/lib/six_timapi/timapi.js',
            'pos_six/static/src/js/BalanceButton.js',
            'pos_six/static/src/js/Chrome.js',
            'pos_six/static/src/js/models.js',
            'pos_six/static/src/js/payment_six.js',
            'pos_six/static/src/xml/**/*',
        ],
    }
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
}
