# -*- coding: utf-8 -*-
{
    'name': "Add Lines Details",
    'version': '14.0.1.0.1',
    'category' : 'Audit',
    'license': 'Other proprietary',
    'summary': """Add Survey to Audit.""",
    'author': "CorpoEureka",
    'website': "http://www.corpoeureka.com",
    'description': """
Add Survey Options to Audit
    """,
    'depends': [
                'base',
                'sale_management',
                'account',
                'purchase',
                'survey',
                'odoo_audit_request_form',
                ],
    'data':[
       'security/ir.model.access.csv',
       'views/custom_audit_request_view.xml',
       'views/survey_survey_view.xml',
       'views/survey_question_template.xml',
       'report/survey_report.xml',
    ],
    'installable' : True,
    'application' : False,
}