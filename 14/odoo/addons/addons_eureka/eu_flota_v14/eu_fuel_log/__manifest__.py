# -*- coding: utf-8 -*-
{
    'name': "Registro de combustible",
    'summary': "Registro de combustible por vehículo",
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'category': 'Human Resources/Fleet',
    'version': '1.0',
    'depends': ['base', 'fleet_operations'],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_views.xml',
    ],
}