# -*- coding: utf-8 -*-
{
    'name': "eu_acuerdo_liquidacion",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'account', 'eu_multi_currency', 'eu_agroindustry'],
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/account_payment_views.xml',
        'views/chargue_consolidate_views.xml',
        'views/acuerdo_liquidacion_views.xml',
    ],
}
