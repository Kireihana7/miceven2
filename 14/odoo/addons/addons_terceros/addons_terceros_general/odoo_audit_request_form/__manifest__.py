# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Audit Request Form (Internal and External)',
    'version': '4.2.3',
    'category': 'Accounting/Accounting',
    'price': 99.0,
    'currency': 'EUR',
    'summary': """Internal and External Audit Request and Flow""",
    'description': """
Audit Request Form (Internal and External)
Internal and External Audit Request and Flow
internal audit
external audit
erp audit
account audit
accouting audit
journal entry audit
audit request
audit request form
odoo audit
audit odoo
employee audit
sales audit
report audit
audit report
    """,
    'license': 'Other proprietary',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_audit_request_form/993',#'https://youtu.be/A_rTHh-WBHg',
    'images': ['static/description/image.png'],
    'support': 'contact@probuse.com',
    'depends': ['mail', 'base', 'mail_bot', 'hr', 'branch', 'eu_hr_department_logo'],
    'data': [
        'security/audit_request_security.xml',
        'security/ir.model.access.csv',
        'report/report_audit_request_action.xml',
        'report/report_header_memo_audit.xml',
        'report/report_memo_audit_template.xml',
        'report/report_audit_planning.xml',  
        'report/report_audit_new.xml',
        'report/report_audit_request_template.xml',        
        'data/templates.xml',
        'data/audit_sequence_data.xml',
        'data/audit_category_data.xml',

        # Wizard
        'wizard/registrar_hallazgo_views.xml',
        'wizard/alternar_hallazgo_views.xml',
        'wizard/audit_refuse.xml',

        # Views
        'views/audit_request.xml',
        'views/audit_category.xml',
        'views/assets.xml',
        'views/audit_tag.xml',
        'views/audit_action_views.xml', 
        'views/audit_documentation_views.xml', 
        'views/audit_finding_views.xml', 
        'views/audit_activities_views.xml', 
        'views/audit_plan_views.xml', 
        'views/audit_request_form_actions.xml', 
        'views/audit_request_form_menus.xml', 
        'views/inherited_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'qweb': [
        'static/xml/index.xml',
    ]
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
