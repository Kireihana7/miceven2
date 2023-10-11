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
    'name': "Instant and Manual Multi Currency",
    'version': '14.0.1.0',
    'category' : 'Account - Facturación',
    'summary': """Esta aplicación permite visualizar otra moneda en la vista de Facturación.""",
    'website': "http://www.corpoeureka.com",
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'license' : 'OPL-1',
    'description': """
Esta APP permite visualizar y calcular otro campo Total en la vista de Facturación
Permitiendo mostrar el total en otra divisa
    """,
    'depends': [
                'account',
                'sale',
                'purchase',
                'sr_manual_currency_exchange_rate',
                'analytic',
                'account_budget',
                ],
    'data':[
       'views/product_pricelist_view.xml',
       'views/product_pricelist_item_view.xml',
       'views/res_currency_view.xml',
       'views/res_currency_rate_view.xml',
       'views/account_move_view.xml',
       'views/account_move_line_view.xml',
       'views/account_payment_view.xml',
       'views/sale_order_view.xml',
       'views/sale_order_line_view.xml',
       'views/purchase_order_view.xml',
       'views/purchase_order_line_view.xml',
       'views/account_analytic_line_view.xml',
       'views/account_analytic_account_view.xml',
       'views/account_budget_view.xml',
       'views/account_bank_statement_view.xml',
       'views/account_reconcile_model_view.xml',
    ],
    'installable' : True,
    'application' : False,
}