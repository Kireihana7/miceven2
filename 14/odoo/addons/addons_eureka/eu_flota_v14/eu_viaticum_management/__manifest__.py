# -*- coding: utf-8 -*-
{
    'name': "eu_viaticum_management",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'eu_multi_currency'],
    'data': [
        'security/ir.model.access.csv',
        'views/viaticum_viaticum_actions.xml',
        'views/viaticum_viaticum_menus.xml',
        'views/viaticum_viaticum_views.xml',
        'views/inherited_views.xml',
        'report/viaticum_report.xml',
        'security/security.xml',
    ],
}
