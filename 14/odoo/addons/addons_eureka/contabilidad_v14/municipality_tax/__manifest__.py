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
    'name': 'Municipal Taxes for Venezuela Localization',
    'version': '14.0.0.1',
    'author': 'CorpoEureka',
    'description': 'Municipal Taxes',
    'category': 'Account',
    'depends': [
        'account',
        'mail',
        'account_accountant',
        'base',
        'l10n_ve_fiscal_requirements',
        'l10n_ve_dpt',
        'eu_template_report_corpoeureka',
        'eu_multi_currency',
        ],
    'data': [
        'security/ir.model.access.csv',
        'security/multi_company.xml',
        'data/seq_muni_tax_data.xml',
        'data/period.month.csv',
        'data/period.year.csv',
        'views/res_config_view.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/res_partner_views.xml',
        'views/municipality_tax_views.xml',
        'views/tax_municipal_declaration_view.xml',
        'report/report_municipal_tax.xml',
        'report/iae_report.xml',
        'report/iae_template.xml',
        'data/muni_mail_template_data.xml',
        'views/res_company_views.xml',
        'views/menu_item.xml',
        'views/iae_wizard_view.xml',
        'wizard/wizard_payment_retention.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
