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

#   Responsable CorpoEureka: Ford-Ndji Joseph
##########################################################################-
{
    'name': "eu_payroll_branch_report",
    'description': """
        Reporte nominal por sucursal
    """,
    'version': '14.0.1.0',
    'summary': '',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'category': 'Payroll',
    'depends': [
                'hr',
                'stock','account',
                'hr_attendance',
                'hr_holidays',
                'hr_payroll',
                'hr_payroll_account',
                'l10n_ve_dpt',
                'l10n_ve_retencion_islr',
                'eu_dom_payroll',
                'eu_personal_info',
                'eu_contract_add_fields',
                'eu_payroll_employee_name',
                'eu_employee_cost_centers',
                'eu_datos_rrhh',
                'eu_special_struct',
                'eu_datos_familiares',
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/payroll_branch_report_wizard.xml',
        'reports/payroll_branch_report.xml',
        'reports/payroll_branch_report_template.xml',
    ],

    'installable': True,
}
