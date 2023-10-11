# -*- coding: utf-8 -*-

{
    'name': "Requisición, Integración con el módulo de Mantenimiento",
    'version': '13.0.1.0',
    'category' : 'Maintenance',
    'license': 'Other proprietary',
    'summary': """Esta aplicación permite realizar una Requisición desde la ventana de Mantenimiento.""",
    'author': "CorpoEureka",
    'website': "http://www.corpoeureka.com",
    'description': """
Esta App permite añadir una Requisición en la Ventana de Mantenimiento
Botón inteligente en Mantenimiento
    """,
    'depends': [
                'maintenance',
                'material_purchase_requisitions',
                'base_maintenance',
                ],
    'data':[
       'views/material_purchase_requisition_view.xml',
       'views/maintenance_view.xml',
    ],
    'installable' : True,
    'application' : False,
}
