#-*- coding:utf-8 -*-
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

#   Responsable CorpoEureka: CorpoEureka
##########################################################################-
{
    'name': "eu_kaly_payroll_report",
    'summary': """
       """,
    'description': """
        Report payroll of proof of work
    """,
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'category': 'Uncategorized',
    'version': '14.0.1.0',
    'depends': [
        'base',
        'hr_contract',
        'hr_holidays',
        'hr_work_entry',
        'eu_dom_payroll',
        'hr_payroll',
        'eu_special_struct',
        'mail',
        'web_dashboard',
        'l10n_ve_payroll',
        'l10n_ve_dpt',
        'l10n_ve_account_SH',
    ],

    'data': [
        'security/ir.model.access.csv',
        'reports/reports_payroll.xml',
        'reports/report_proof_work_template.xml',
        'reports/header_registro_patronal_asegurados.xml',
        'reports/report_patronal_asegurados.xml',


        'views/proof_work_payroll_form.xml',
        'wizard/registro_patronal_asegurados_wizard.xml',
    ],
    'installable': True,
    
}
