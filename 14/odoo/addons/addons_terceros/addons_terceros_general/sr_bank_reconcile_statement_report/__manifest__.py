# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': 'Bank Reconciliation Statement Report',
    'version': '14.0.0.0',
    'category': 'Accounting',
    "license": "OPL-1",
    'summary': 'Bank Reconciliation Statement Report print bank account statement account reconciliation statement report bank statement report report with credit and debit reconciliation report with accounts credit and debits',
    'description': """
    Bank Reconciliation Statement Report
    print bank account statement
    account reconciliation statement
    report bank statement
    report with credit and debit
    reconciliation report with accounts credit and debits
    print statement
    print bank statement
    bank reconciliation statement report
    pdf report
    statement pdf report 
    bank reconciliation pdf report
    bank reconciliation statement
    reconciliation process
    bank statement reconciliation
    print statement report with account
    print statement report with debit and credit
    print bank reconciliation statement report with accounts
    print bank reconciliation statement report with debit and credit
    
""",
    "price": 12,
    "currency": 'EUR',
    'author': 'Sitaram',
    'depends': ['account'],
    'data': [
        "reports/sr_bank_reconcile_statement_report_template.xml",
        "reports/sr_bank_reconcile_statement_report.xml",
        
    ],
    'website':'https://sitaramsolutions.in',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/xHcaseChuq0',
    "images":['static/description/banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
