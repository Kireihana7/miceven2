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

#   Responsable CorpoEureka: Ricardo Sanchez
##########################################################################-
{
    'name': "Salesperson Traccar",
    'summary': "Seguimiento via GPS para vendedores.",
    'author': "CorpoEureka",
    'license' : 'OPL-1',
    'website': "http://www.yourcompany.com",
    'category': 'Tools',
    'version': '14.0.1.0',
    'depends': [
        'base', 
        'hr', 
        'eu_sales_visit',
        'eu_sales_kpi_kg',
        'base_geolocalize',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'wizard/salesperson_raise_message.xml',
        'wizard/wizard_salesperson_traccar_fetch_trips.xml',
        'wizard/wizard_salesperson_traccar_device_summary.xml',
        'wizard/wizard_salesperson_traccar_fetch_routes.xml',
        'wizard/wizard_salesperson_traccar_device_location.xml',
        'views/assets.xml',
        'views/hr_traccar_employee_views.xml',
        'views/hr_traccar_config_settings_views.xml',
        'views/hr_employee_views.xml',
        'views/salesperson_traccar_trip_details.xml',
        'views/salesperson_traccar_route_details.xml',
        'views/salesperson_traccar_event_details.xml',
    ],
    "qweb": [
        "/eu_salesperson_traccar/static/src/xml/*.xml",
    ],
}
