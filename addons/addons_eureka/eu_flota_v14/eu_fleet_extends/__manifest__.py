# -*- coding: utf-8 -*-
{
    'name': "eu_fleet_extends",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'fleet_operations','material_purchase_requisitions'],
    'data': [
        'views/views.xml',
    ],
}
