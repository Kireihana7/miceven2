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
    'name': 'Gestión de tráfico e inventario ',
    'version':'1.0',
    'category': 'Inventory',
    'author': 'CorpoEureka',
    'category': 'Sale',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'license' : 'OPL-1',
    'description': """

    """,
    'depends':[
        'eu_quality_inspection',
        'eu_multi_currency',
        'l10n_ve_fiscal_requirements',
    ],
    'data':[
        
        # Assets
        'views/chargue_consolidate_asset.xml',

        # Secuencias de las Guías de Despacho
        'data/sequence.xml',
        'data/security_group.xml',
        
        #Permiso de Acceso
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Multi Company
        'security/security_multi_company.xml',
        
        # Wizards
        'wizard/chargue_consolidate_reason_view.xml',
        'wizard/chargue_consolidate_picking_view.xml',
        'wizard/chargue_consolidate_link_picking_view.xml',
        'wizard/chargue_manual_view.xml',
        'wizard/peso_liquidar_operation_views.xml',
        'wizard/chargue_consolidate_excedente_wizard_view.xml',
        'wizard/chargue_consolidate_descuento_wizard_view.xml',
        
        # Vistas Creadas y Heredadas
        'views/account_move_views.xml',
        'views/chargue_consolidate_excedente_view.xml',
        'views/chargue_consolidate_descuento_view.xml',
        'views/hr_employee_view.xml',
        'views/romana_serial_view.xml',
        'views/product_product_view.xml',
        'views/chargue_consolidate_without_view.xml',
        'views/stock_picking_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/quality_control_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/res_users_view.xml',
        'views/chargue_consolidate_cancel_view.xml',
        'views/chargue_multi_weight_view.xml',
        'views/seed_type_views.xml',
        'views/stock_move_views.xml',
        'views/stock_move_line_views.xml',
        'views/res_config_settings_views.xml',
        'views/chargue_consolidate_pesaje_externo_views.xml',
        'views/tabla_deduccion_views.xml',
        'views/menuitem_view.xml',
        
        #Reportes 
        'reports/template_pesaje_romana.xml',
        'reports/boleto_pesaje_romana.xml',
        'reports/agroindustry_order_chargue.xml',
        'reports/qa_romana_report.xml',
    ],
    'qweb': [
        'static/src/xml/chargue_consolidate_dashboard.xml',
    ],
    'images': ['static/description/images/dispatch-guide.png'],
    'installable': True,
    'application': True
}
