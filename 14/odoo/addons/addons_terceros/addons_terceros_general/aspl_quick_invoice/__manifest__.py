# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Quick Invoice (Fast Invoice) (Enable with Barcode Scanner) (Community)',
    'category': 'Point of Sale',
    'summary': 'This module allows user to create quick invoice.',
    'description': """
This module allows user to to create quick invoice.
""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 99.00,
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': ['base','account','barcodes','web','eu_multi_currency','eu_account_series'],
    'images': ['static/description/main_screenshot.png'],
    "data": [
        'views/aspl_quick_invoice_template.xml',
        'views/quick_invoice_view.xml',
    ],
    'qweb': [
        'static/src/xml/quick_invoice.xml',
        'static/src/xml/quick_invoice_dialogs.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: