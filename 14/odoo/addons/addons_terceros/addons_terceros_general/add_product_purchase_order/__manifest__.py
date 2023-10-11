# -*- coding: utf-8 -*-
#######################################################

#   CorpoEureka - Innovation First!
#
#   Copyright (C) 2021-TODAY CorpoEureka (<https://www.corpoeureka.com>)
#   Author: CorpoEureka (<https://www.corpoeureka.com>)
#
#   This software and associated files (the "Software") may only be used (executed,
#   modified, executed after modifications) if you have pdurchased a vali license
#   from the authors, typically via Odoo Apps, or if you have received a written
#   agreement from the authors of the Software (see the COPYRIGHT file).
#
#   You may develop Odoo modules that use the Software as a library (typically
#   by depending on it, importing it and using its resources), but without copying
#   any source code or material from the Software. You may distribute those
#   modules under the license of your choice, provided that this license is
#   compatible with the terms of the Odoo Proprietary License (For example:
#   LGPL, MIT, or proprietary licenses similar to this one).
#
#   It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#   or modified copies of the Software.
#
#   The above copyright notice and this permission notice must be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

#   Responsable CorpoEureka: Jose Mazzei
##########################################################################-
{
    "name": "Add Multiple Product From Purchase Order",
    "version": "14.0.1.0",
    "summary": "Using this module you can add multiple product on purchase order. | purchase Cart | Add Product on purchase | Product Cart | purchase Order | add product on purchase | purchase cart | quick add product | Product add widget | Add purchase Order Line In Batch | Mass Product | Mass add product | product widget",
    "description": """Using this module you can add product on purchase order.""",
    "license": 'OPL-1',
    "category": 'purchase',
    "author": 'CorpoEureka',
    "depends": [
        'purchase',
        'stock',
        'uom',
        'eu_multi_currency',
        'eu_third_payment',
        'purchase_payment',
        'eu_account_payment_add_date',
        'eu_add_field_partner',
        'purchase_stock',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/assets.xml',
        'views/purchase_view.xml',
        'views/product_saco_view.xml',
        'views/stock_picking_type_view.xml',
        'views/product_kanban_view.xml',
        'views/report_payment_receipt.xml',
        'views/report_purchaseorder_new.xml',
        'views/account_payment_view.xml',
        'views/stock_move_view.xml',
    ],
    'images': ['static/description/banner.gif'],
    "installable": True,
}
