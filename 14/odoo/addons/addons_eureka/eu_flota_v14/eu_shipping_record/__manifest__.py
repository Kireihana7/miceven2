# -*- coding: utf-8 -*-
{
    'name': "Registor de viajes",
    'summary': "Bitácoras de viajes por vehículo",
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'category': 'Human Resources/Fleet',
    'version': '1.0',
    'depends': [
        'base',
        'fleet_operations',
        'stock', 
        'contacts',
        'branch',
        'sale_management',
        'eu_secondary_uom',
        "l10n_ve_fiscal_requirements",
        "eu_fuel_log",
        "eu_fleet_group",
        'eu_viaticum_management',
        'eu_picking_guide',
    ],
    'data': [
        'security/ir.model.access.csv',

        # Views
        'views/fleet_trip_views.xml',
        'views/account_move_views.xml',
        'views/fleet_trip_type_views.xml',
        'views/fleet_trip_lines_views.xml',
        'views/fleet_trip_product_views.xml',
        'views/fleet_trip_milestone_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/eu_shipping_record_actions.xml',
        'views/eu_shipping_record_menus.xml',
        'views/res_config_settings_views.xml',
        'views/assets.xml',

        # Wizard
        'wizard/do_transhipment_views.xml',

        # Reports
        'reports/eu_shipping_record_reports.xml',
        'reports/report_header_trip_driver.xml',
        'reports/report_trip_driver_template.xml',
    ],
    'qweb': [
        'static/src/xml/TripDashboard.xml'
    ]
}