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
    'name': 'Reglas Salariales',
    'category': 'Nomina/Reglas Salariales',
    'summary': 'Registro de las reglas salariales',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'version': '14.0.1.0',
    'description': "",
    'depends': [
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
        'data/account.account.csv',
        'data/hr_payroll_category_data.xml',
        'data/hr_payroll_nomina_quincenal_data.xml',
        'data/hr_payroll_vacaciones_data.xml',
        'data/hr_payroll_nomina_semana_data.xml',
        'data/hr_payroll_utilidades_data.xml',
        'data/hr_payroll_liquidation_data.xml',
        'data/hr_payroll_beneficio_data.xml',
        'data/hr_payroll_prestamo_data.xml',
        'data/hr_payroll_horas_extras_data.xml',
        'data/hr_payroll_nomina_eventual_data.xml',
        'data/hr_payroll_cesta_ticket_data.xml',
        'data/hr_payroll_provisiones_data.xml',
        'data/hr_payroll_honorarios_profe_data.xml',
        'data/hr_payroll_input_type_data.xml',

    ],
    'installable': True,
    'application': True,
}
