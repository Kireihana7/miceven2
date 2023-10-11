# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Israel - Accounting',
    'version': '1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
This is the latest basic Israelian localisation necessary to run Odoo in Israel:
================================================================================

This module consists of:
 - Generic Israel Chart of Accounts
 - Taxes and tax report
<<<<<<< HEAD
 - Multiple Fiscal positions
=======
 - Fiscal position for Palestina
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
 """,
    'website': 'http://www.odoo.com/accounting',
    'depends': ['l10n_multilang'],
    'data': [
        'data/account_chart_template_data.xml',
<<<<<<< HEAD
        'data/account_tax_group_data.xml',
        'data/account_account_tag.xml',
        'data/account.account.template.csv',
        'data/account.group.template.csv',
=======
        'data/account_account_tag.xml',
        'data/account.account.template.csv',
        'data/account_data.xml',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        'data/account_tax_report_data.xml',
        'data/account_tax_template_data.xml',
        'data/fiscal_templates_data.xml',
        'data/account_chart_template_post_data.xml',
        'data/account_chart_template_configure_data.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}
