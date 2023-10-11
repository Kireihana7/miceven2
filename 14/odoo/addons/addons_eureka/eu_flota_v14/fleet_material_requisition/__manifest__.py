# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Requisición, Integración con el módulo de Flota",
    'version': '1.0',
    'category' : 'Fleet - Flota',
    'license': 'Other proprietary',
    'summary': """Esta aplicación permite realizar una Requisición desde la venta de Flota.""",
    'author': "Corpo Eureka C.A - Jose Mazzei.",
    'website': "http://www.corpoeureka.com",
    'description': """
Esta App permite añadir una Requisición en la Ventana de Flota
Botón inteligente en Flota
    """,
    'depends': [
                'fleet',
                'material_purchase_requisitions',
                ],
    'data':[
       'views/material_purchase_requisition_view.xml',
       'views/project_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
