# encoding: UTF-8
{
    'name': 'Impuesto a las Grandes Transacciones Financieras',
    'version':'1.0',
    'category': 'Account',
    'summary':'Automatic ITF Withhold',
    'description': '''\
Calculate automatic itf withholding
===========================
Colaborador: Jose Mazzei

V1.0
Calculate automatic itf withholding
''',
    'author': 'Corpoeureka',
    'website': 'https://www.corpoeureka.com/web/soluciones/odoo',
    'data': [
        'security/ir.model.access.csv',
        'view/res_company_view.xml',
        'view/account_journal_view.xml',
        'view/account_payment_view.xml',
        #'view/advance_payment_view.xml',
        'view/wizard_igtf_report.xml',
        'view/igtf_declaration_view.xml',
        'wizard/account_payment_igtf_view.xml',
        'reports/igtf_template.xml',
        'reports/declaration_template.xml',
        'data/sequence.xml',
    ],
    'depends': ['base','account','sr_manual_currency_exchange_rate'],
    'images': ['static/description/image/icon_eu.png'],
    'application': True,
}