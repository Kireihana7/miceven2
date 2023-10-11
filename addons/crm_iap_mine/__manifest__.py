# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Lead Generation',
    'summary': 'Generate Leads/Opportunities based on country, industries, size, etc.',
    'category': 'Sales/CRM',
    'version': '1.2',
    'depends': [
        'iap_crm',
        'iap_mail',
    ],
    'data': [
        'data/crm.iap.lead.industry.csv',
        'data/crm.iap.lead.role.csv',
        'data/crm.iap.lead.seniority.csv',
        'data/mail_template_data.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/crm_iap_lead_mining_request_views.xml',
        'views/res_config_settings_views.xml',
        'views/mail_templates.xml',
        'views/crm_menus.xml',
    ],
    'auto_install': True,
<<<<<<< HEAD:addons/crm_iap_mine/__manifest__.py
    'assets': {
        'web.assets_backend': [
            'crm_iap_mine/static/src/js/**/*',
            'crm_iap_mine/static/src/views/*.js',
            'crm_iap_mine/static/src/views/*.xml',
        ],
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/crm_iap_lead/__manifest__.py
    'license': 'LGPL-3',
}
