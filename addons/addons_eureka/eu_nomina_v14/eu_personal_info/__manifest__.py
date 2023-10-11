# -*- encoding: UTF-8 -*-

# -----------------------------------------------------------------------------
{
    'name': 'Información Personal',

    'summary': """
        Este módulo fue diseñado para añadir todo tipo de información personal
        concerniente de sus empleados.""",

    
    'description': '''\
Agrega nuevos campos y funcionalidades a la ficha del empleado.\n

''',
    'version': '14.0.1.0',
    'website': "http://www.corpoeureka.com",
    'support': 'proyectos@corpoeureka.com',
    'author': "CorpoEureka",
    'license' : 'OPL-1',
    'category': 'Human Resources/Payroll',
    'data': [
        'security/ir.model.access.csv',
        'views/hr_personal_info_view.xml',
        ],
    'depends': ['hr','l10n_ve_dpt'],
    'installable': True,

}
