# -*- coding: utf-8 -*-
{
    'name': "eu_fleet_maintenance",
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
    'depends': [
        'base', 
        'fleet_operations',
        'eu_vehicle_inspection',
        'mro_maintenance',
        'mrp_mro_integration',
    ],
    'data': [
        'security/multi_company_rules.xml',
        'views/fleet_views.xml',
        'views/mro_request_views.xml',
    ],
}
