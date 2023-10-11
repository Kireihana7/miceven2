# -*- coding: utf-8 -*- Ñeri here
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Archivar Productos y contactos alpha',
    'category': 'Misc',
    'sequence': 150,
    'summary': '',
    'author': 'José Ñeri, CorpoEureka',
    'description': """
Te permite archivar productos y contactos!
""",
    'depends': [
        'base', 'stock'],
    'data': [
        'security/security.xml',
        'views/template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
