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
    'name': "Instalador de Contabilidad Eureka",
    'summary': """
        Facilita la Instalación de los Addons Contables""",
    'description': """
        Facilita la Instalación de los Addons Contables
    """,
    'author': "CorpoEureka",
    'website': "http://corpoeureka.com/",
    'company': 'CorpoEureka',
    'category': 'Account',
    'version': '14.0.0.1',
    'license':'OPL-1',
    'depends': [
        'base', 
        'account',
        #'branch',
        'eu_firma_digital',
        'eu_template_report_corpoeureka',
        'eu_account_payment_add_date',
        'sr_manual_currency_exchange_rate',
        'account_budget',
        'eu_multi_currency',
        'l10n_ve_fiscal_requirements',
        'l10n_ve_dpt',
        'l10n_ve_currency_rate',
        'eu_account_series',
        'l10n_ve_account_SH',
        'l10n_ve_retencion_iva',
        'l10n_ve_retencion_islr',
        'eu_numero_impor_expor',
        'l10n_ve_accountant',
        'eu_account_invoice_parent',
        'eu_libros_contables_xls',
        'municipality_tax',
        'eu_municipal_tax',
        'eu_legal_daily',
        'eu_daily_conciliation',
        'account_daily_consolidate',
        'sh_sync_fiscal_year',
    ],
    'data': [
    ],
    "installable": True,
}
