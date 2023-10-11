# -*- coding: utf-8 -*-
{
    
    'name': "Solicitud de Prestaciones",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        esta aplicacion, crea la solicitud de prestaciones
    """,

    'author': "CorpoEureka",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'mail',
        'base', 
        'hr',
        'l10n_ve_payroll'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/request_benefists_view.xml',
        'views/reason_service.xml',
        'report/acttion_report_prestaciones.xml',
        'report/template_report_prestaciones.xml',

        
    ],
    # only loaded in demonstration mode
    'demo': [

       
    ],
}