# -*- coding: utf-8 -*-
{
    'name': "Maintenance Extend",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "CorpoEureka",
    'website': "http://www.corpoeureka.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','eu_maintenance_damages'],
    'data': [
        'views/correlative_view.xml',
        'views/company_sequence.xml',
        'views/correlative_list_view.xml',
        'data/ir_sequence.xml',
    ],
}
