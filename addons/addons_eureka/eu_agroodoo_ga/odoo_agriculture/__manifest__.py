# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Agriculture / Farm Management',
    'version': '2.1.2.3',
    "sequence": -300,
    'category': 'Project',
    'price': 149.0,
    'currency': 'USD',
    'license': 'Other proprietary',
    'summary': "Agriculture / Farm Management Software",
    'description': """ 
        Agriculture app
        Agriculture Management
        Crop Requests
        Crops
        crop
        Agriculture Management Software
        Incidents
        Diseases Cures
        agribusiness
        crop yield
        agriculture institutes
        Farmers
        AMS
        Farm Locations
        farmers
        farmer
        Agriculture odoo
        odoo Agriculture
        Agriculture Management System
        Animals
        print Crop Requests Report
        print Crops Report
        odoo Agriculture Management Software
        Farm Management Software

        """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://youtu.be/LJwRVOhkK3I',
    'depends': [
        'account',
        'project',
        'stock',
        'website_customer',
        'maintenance',
        'fleet',
        'material_purchase_requisitions',
        'sh_po_tender_management',
        'purchase',
        'analytic',
        'agrodoo_helper',
        'account_budget',
        # 'analytic_account_dashboard_map',
    ],
    
    'data': [
        # Security:
        'security/agriculture_security.xml',
        'security/ir.model.access.csv',
        # Data:
        'data/ir_sequence_data.xml',
        'data/default_records.xml',
        
        # Wizards:
        'wizard/crop_request_records_requisition_views.xml',
        'wizard/crop_project_template_transactions_views.xml',
        'wizard/assign_agriculture_seq_wizard_views.xml',

        # Reports:
        'report/farmer_cropping_request_report.xml',
        'report/farmer_location_crops_report.xml',
        
        # Views:
        'views/res_partner_view.xml',
        'views/crops_view.xml',
        
        'views/crops_material_job_view.xml',
        'views/crops_dieases_view.xml',

        'views/project_view.xml',
        'views/crop_project_template_views.xml',
        
        'views/crops_animals_view.xml',
        'views/google_map_template_view.xml',
        'views/crops_fleet_view.xml',
        'views/crops_incident_view.xml',
        'views/crops_tasks_template_view.xml',
        
        'views/farmer_cropping_request_view.xml',
        'views/material_purchase_requisition_view.xml',
        'views/purchase_agreement_views.xml', # Heredado
        'views/stock_picking_views.xml', # Heredado
        'views/purchase_views.xml', # Heredado
        'views/sale_views.xml', # Heredado
        'views/account_move_views.xml', # Heredado
        'views/analytic_account_views.xml', # Heredado

        'views/menu_item.xml',
        'views/agriculture_cost_sheet_views.xml',
        'views/agriculture_workday_spreadsheet_views.xml',        
        'views/job_type_views.xml',
        'views/crops_tipos_suelo_view.xml',
        'views/agriculture_parcelas_view.xml',
        'views/agriculture_tablon_view.xml',
        'views/agriculture_fincas.xml',
        'views/product_template_views.xml', # Heredado
        
        'views/maintenance_views.xml', # Heredado
        'views/res_company_views.xml', # Heredado
        
        'views/equipment_reservation_views.xml',
        'views/labour_management_views.xml',
        'views/crop_material_management_views.xml',
        'views/crop_request_transaction_views.xml',
        
        'views/seed_variety_views.xml', # Heredado
        'views/fleet_vehicle_views.xml', # Heredado
        'views/fleet_vehicle_model_views.xml', # Heredado
    ],
    'installable' : True,
    'application' : False,
    'post_init_hook': '_insert_default_crop_types'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
