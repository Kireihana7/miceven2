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
    'name': "Nómina Venezuela",
    'version': '1.1',
    'summary': """Esta aplicación permite visualizar otra moneda en la vista de Nómina.""",
    'description': """
Esta APP permite visualizar y calcular otro campo Total en la vista de Nómina
Permitiendo mostrar el total en otra divisa
    """,
    'website': "http://www.corpoeureka.com",
    'support': 'proyectos@corpoeureka.com',
    'author': "CorpoEureka",
    'license' : 'OPL-1',
    'category': 'Human Resources/Payroll',
    'depends': [
                'hr','documents_hr',
                'mail',
                'documents_hr_payroll',
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
                # 'queue_job',
                ],
    'data':[
        'data/data_conceptos.xml',
        'data/secuencia.xml',
        'static/src/xml/templates.xml',
        'security/groups_lvls.xml',
        'views/hr_payroll_view.xml',
        'report/action_report_constacia_trabajo.xml',
        'report/report_constancia_trabajo.xml',
        'views/res_company.xml',
        'views/report_payslip_templates.xml',
        'views/hr_payroll_report.xml',
        'data/email_template.xml',
        'views/hr_payslip_tree.xml',
        'views/hr_self_vacation_payslip_views.xml',
        'views/hr_contract_view.xml',
        'views/hr_employee_views.xml',
        'views/hr_payroll_run_view.xml',
        'views/account_journal_view.xml',
        'views/hr_charged_vacation_holidays_views.xml',
        'views/hr_prestaciones_views.xml',
        'views/hr_anticipos_views.xml',
        'views/hr_liquidaciones_view.xml',
        'views/hr_utilities_views.xml',
        'views/hr_structure_view.xml',
        'views/hr_beneficios.xml',
        'views/hr_job_view.xml',
        'views/hr_resource_calendar.xml',
        'views/hr_lista_vacaciones_vencidas.xml',
        'views/hr_employees_journey_groups_view.xml',
        'views/hr_prestaciones_lines_views.xml',
        'views/act_tasa_wiz.xml',
        'views/hr_bonification_per_employee.xml',
        'report/template_report_nomina_new.xml',
        'report/template_reports_extra.xml',
        'report/action_report_canario.xml',
        'report/action_report_extra_reports.xml',
        'wizard/nomina_global_wizard_views.xml',
        'wizard/renew_contract_wizard_view.xml',
        'wizard/mass_wages_changer_view.xml',
        'wizard/report_inces_wizard_view.xml',
        'wizard/report_faov_wizard_view.xml',
        'wizard/select_faov_wizard.xml',
        'wizard/create_pay_compromise_wiz_view.xml',
        'wizard/config_prestaciones_wizard_views.xml',
        'wizard/config_configuraciones_company.xml',
        'wizard/constancia_trabajo_wizard_view.xml',
        'wizard/import_holiday_calendar.xml',
        'wizard/incidences_creator_view.xml',
        'wizard/report_listado_egreso_y_activos_view.xml',
        'data/server_actions.xml',
       
       'security/security_multi_company.xml', 
       'security/ir.model.access.csv',
    ],
    'external_dependencies': {
      'python': [
        'Pyzipper',
        # 'xlsxwriter',
        #'numpy', 
        #'numpy-financial'
      ]
    },
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
