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

#   Responsable CorpoEureka: José Ñeri
##########################################################################-
{
    'name': "Base for Payroll with loans",

    'summary': """This module adapts Odoo Payroll and HHRR modules to better use""",

    'description': """
    'license' : 'OPL-1',
    """,

    'version': '14.0.1.0',
    'category': 'Localization/Payroll',
    'website': "http://www.corpoeureka.com",
    'support': 'proyectos@corpoeureka.com',
    'author': "CorpoEureka",
    'depends': ['base',
                'hr',
                'hr_payroll',
                'hr_payroll_account',
                'contacts',
                'account'],

    # always loaded
    'data': [
        # 'data/res_partner.xml',
        'data/contribution_registers.xml',
        # 'data/salary_structure.xml',
        'data/salary_rules_categories.xml',
        'data/salary_rule_inputs.xml',
        # 'data/salary_rules.xml',
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        'views/hr_payslip_view.xml',
        'views/hr_payroll_structure.xml',
        'views/hr_payslip_run_view.xml',
        'views/hr_employee_loan_views.xml',
        'views/hr_employee_views.xml',
        'views/payslip_report_templates.xml',
        'views/mail_templates.xml',
        'views/discount_import_views.xml',
        'views/working_hours_import_views.xml',
        'wizard/payslip_report_wizard_view.xml',
        'wizard/ministry_of_labour_report_wizard_view.xml',
    ],
    'external_dependencies': {
      'python': [
        'xlsxwriter',
        'dateutil', 
      ]
    },
}