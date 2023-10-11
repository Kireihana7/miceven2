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
    "name": "Gestión de retenciones sobre IVA según las leyes venezolanas",
    "version": "14.0.0.1",
    'author': 'CorpoEureka',
    "category": 'Account',
    "depends": [
        'base',
        'account',
        'l10n_ve_account_SH',
        'account_debit_note',
        'eu_multi_currency',
        'branch',
    ],
    'data': [
        'security/security_group.xml',
        'wizard/declare_pay_iva.xml',
        'wizard/wh_export_iva_txt.xml',
        'report/report.xml',
        'report/wh_iva_receipt_template.xml',
        'views/account_invoice_view.xml',
        'views/wh_iva_view.xml',
        'views/account_view.xml',
        'views/res_config_view.xml',
        'views/retention_IVA.xml',
        'views/account_payment_view.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/fiscal_position_data.xml',
        'security/security_multi_company.xml',
        'data/wh_mail_template_data.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}