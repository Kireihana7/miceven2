# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Peru - Accounting',
    "version": "3.0",
    'summary': "PCGE Simplified",
    'category': 'Accounting/Localizations/Account Charts',
    'author': 'Vauxoo, Odoo',
<<<<<<< HEAD
    'website': 'https://www.odoo.com/documentation/16.0/applications/finance/accounting/fiscal_localizations/localizations/peru.html',
=======
    'website': 'https://www.odoo.com/documentation/user/14.0/accounting/fiscal_localizations/localizations/peru.html',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
    'depends': [
        'base_vat',
        'base_address_extended',
        'l10n_latam_base',
        'l10n_latam_invoice_document',
        'account_debit_note',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_tax_view.xml',
        'data/l10n_pe_chart_data.xml',
        'data/account.group.template.csv',
        'data/account.account.template.csv',
        'data/l10n_pe_chart_post_data.xml',
        'data/account_tax_group_data.xml',
        'data/account_tax_data.xml',
        'data/fiscal_position_data.xml',
<<<<<<< HEAD
        'data/l10n_latam_document_type_data.xml',
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        'data/account_chart_template_data.xml',
        'data/res.city.csv',
        'data/l10n_pe.res.city.district.csv',
        'data/res_country_data.xml',
        'data/l10n_latam_identification_type_data.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
        'demo/demo_partner.xml',
    ],
}
