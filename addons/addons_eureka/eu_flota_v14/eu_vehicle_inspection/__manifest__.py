# -*- coding: utf-8 -*-
{
    'name': "eu_vehicle_inspection",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'eu_shipping_record'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_inspection_views.xml',
        'views/fleet_vehicle_inspection_views.xml',
        'views/eu_vehicle_inspection_actions.xml',
        'views/eu_vehicle_inspection_menus.xml',
        'reports/ficha_inspections_reports.xml',
        'reports/header_ficha_inspections.xml',
        'reports/ficha_inspections_template.xml',
    ],
}
