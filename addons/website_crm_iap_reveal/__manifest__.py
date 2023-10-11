# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Lead Generation From Website Visits',
    'summary': 'Generate Leads/Opportunities from your website\'s traffic',
    'version': '1.1',
    'category': 'Sales/CRM',
    'depends': [
        'iap_crm',
        'iap_mail',
        'crm_iap_mine',
        'website_crm',
    ],
    'data': [
        'data/ir_cron_data.xml',
        'data/ir_model_data.xml',
        'security/ir_rules.xml',
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/crm_reveal_views.xml',
        'views/res_config_settings_views.xml',
<<<<<<< HEAD:addons/website_crm_iap_reveal/__manifest__.py
        'views/crm_menus.xml',
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/crm_iap_lead_website/__manifest__.py
    ],
    'license': 'LGPL-3',
}
