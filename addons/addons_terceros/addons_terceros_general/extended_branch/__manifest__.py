# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Multiple Branch Unit Operation Setup for All Applications Odoo',
    'version': '14.0.4.1',
    'category': 'Sales',
    'summary': 'Multiple Branch Management Multi Branch app Multiple Unit multiple Operating unit sales branch Sales Purchase branch Invoicing branch billing Voucher branch warehouse branch Payment branch Accounting Reports for single company Multi Branches multi company',
    "description": """
       Multiple Unit operation management for single company Multiple Branch management for single company
      multiple operation for single company branching company in odoo multiple store multiple company in odoo
""",
    'author': 'Corpoeureka',
    "price": 149.00,
    "currency": 'EUR',
    'depends': ['base', 'sale_management', 'purchase', 'stock', 'account', 'purchase_stock','branch'],
    'data': [
        'security/branch_security.xml',
        'views/inherited_res_partner_bank.xml',
        'views/inherited_account_journal.xml',


    ],
    'qweb': [
        'static/src/xml/branch.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/hi1b8kH5Z94',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
