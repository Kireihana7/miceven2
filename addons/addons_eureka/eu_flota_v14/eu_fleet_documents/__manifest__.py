# -*- coding: utf-8 -*-
{
    'name': "Documentos legales en vehículos",
    'summary': "Registrar documentos para los vehículos cómo la licencia de conducir",
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'category': 'Human Resources/Fleet',
    'version': '1.0',
    'depends': ['base', 'eu_documents_registry', 'fleet', 'fleet_operations'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/fleet_vehicle_views.xml',
    ],
}
