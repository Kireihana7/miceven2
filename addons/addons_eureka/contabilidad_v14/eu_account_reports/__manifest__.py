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
    'name': 'Reportes Contables',
    'version': '14.0.1.0',
    'category': 'Account',
    'website': "http://Corpoeureka.com/",
    'company': 'CorpoEureka',
    'author':'CorpoEureka',
    'license':'OPL-1',
    'summary': 'Reportes Varios Contables',
    'depends': [
        'account',
        'board',
        'eu_multi_currency',
        'base',
        'sale',
        'purchase',
        'stock',
    ],
    'data': [
        # Reportes
        'security/ir.model.access.csv',
        'security/security.xml',

        # Vistas 
        'wizard/kaly_reporte_views.xml', #  David Linarez 
        'wizard/account_receivable_fp_general_wizard_views.xml',# Edgar Aldana - 1
        'wizard/report_accounts_receivable_product_wizard.xml', # Manuel Jimenez - 2 
        'wizard/account_payment_multi_currency_wizard.xml', #Ford-Ndji 3
        'wizard/wizard_miceven_pago_balance_wizard.xml', # Jose Ñeri - 4
        'wizard/clientes_prepago_wizard_views.xml',# Edgar Aldana - 5
        'wizard/eu_reporte_payment_date_wizard.xml', # Jose Mazzei - 6
        'wizard/reporte_vendedores_ventas_views.xml', #  David Linarez 7
        'wizard/reporte_vendedores_articulos_views.xml',   #  David Linarez 8
        'wizard/products_sold_vendor_usd_wizard_views.xml',# Edgar Aldana - 9
        'wizard/sale_report_wizard_views.xml', #Ford-Ndji 10
        'wizard/eu_reporte_payment_bank_wizard.xml', # Jose Mazzei - 11


        # Reportes
        'report/report_account_receivable_fp_general.xml',# Edgar Aldana - 1
        'report/template_account_receivable_fp_general.xml',# Edgar Aldana - 1
        'report/tp_report_list_accounts_receivable_product.xml', # Manuel Jimenez - 2
        'report/sale_report_costumer_template.xml', #Ford-Ndji 3
        'report/wizard_miceven_pago_balance.xml', # Jose Ñeri - 4
        'report/report_clientes_prepago.xml',# Edgar Aldana - 5
        'report/template_clientes_prepago.xml',# Edgar Aldana - 5
        'report/eu_reporte_payment_date_report.xml', # Jose mazzei - 6
        'report/reporte_vendedores_ventas_report.xml', # David Linarez 7
        'report/reporte_vendedores_articulos_report.xml', # David Linarez 8
        'report/report_products_sold_vendor_usd.xml',# Edgar Aldana - 9
        'report/template_products_sold_vendor_usd.xml',# Edgar Aldana - 9
        'report/account_payment_multi_currency.xml',#Ford-Ndji 10
        'report/eu_reporte_payment_bank_report.xml', # Jose Mazzei - 11
        'report/paperformat_for_reports.xml', #Ford-Ndji 3/10
        
        
        # Menu Item de Todos los Reportes
        'views/menuitem.xml',
        # Vista de Usuarios:
        'views/res_users_views.xml',
        # Vista de Contactos:
        'views/res_partner_views.xml',        
    ],
    'installable': True,
}
