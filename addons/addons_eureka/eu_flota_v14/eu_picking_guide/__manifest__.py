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
    'name': 'Picking Consolidate Guide ',
    'version':'14.0.1.0',
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
        'base',
        'stock',
        'fleet',
        'sale_management',
        'account',
        'contacts',
    ],
    'data':[
        #Permiso de Acceso
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Secuencias de las Guías de Despacho
        'data/sequence.xml',
        
        # Multi Company
        'security/security_multi_company.xml',
        
        # Vistas Creadas y Heredadas
        'views/guide_consolidate_view.xml',
        'views/stock_picking_view.xml',
        'views/product_template_view.xml',
        'views/product_product_view.xml',
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/partner_zone_view.xml',
        'views/res_partner_view.xml',
        'wizard/guide_consolidate_reprecint_view.xml',
        'views/menuitem_view.xml',

        #Reportes 
        'reports/templates.xml',
        'reports/guide_consolidate_report.xml',
        'reports/guide_consolidate_product.xml',
        'reports/guide_consolidate_su.xml',
    ],
    'images': ['static/description/eureka_banner.png'],
    'installable': True,
    'application': True
}
