# -*- coding: utf-8 -*-
{
    'name': "Documentos legales",
    'summary': "Registrar documentos para los contactos cómo la cédula o la licencia de conducir",
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'category': 'Human Resources/Employees',
    'version': '1.0',
    'depends': ['base', 'contacts', 'hr'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'data/data.xml',
        
        'views/res_document_views.xml',
        'views/res_partner_views.xml',
    ],
}
