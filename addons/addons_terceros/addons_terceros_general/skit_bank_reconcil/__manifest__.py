# -*- coding: utf-8 -*-

{
    'name': 'Bank Reconciliation Report',
    'version': '1.0',
    'author': 'Srikesh Infotech',
    'description': """
            This Module helps to generate Bank Reconciliation report.
    """,
    'category': 'Accounting',
    'license': "AGPL-3",
    'website': 'http://www.srikeshinfotech.com',
    'price'  : 30,
    'currency': 'EUR',    
    'images': ['images/main_screenshot.png'],
    'depends': ['base', 'account'],
    'data': [
             'wizard/reconcil_report_wizard.xml',
             'report/reconcil_report_temp.xml',
             'report/reconcil_report.xml',
             'wizard/difference_amount.xml',
             'views/popup_template.xml',
             'views/bank_reconcil_view.xml',
             'security/ir.model.access.csv',
            ],
    'auto_install': False,
    'application': True,
    'installable': True,
}
