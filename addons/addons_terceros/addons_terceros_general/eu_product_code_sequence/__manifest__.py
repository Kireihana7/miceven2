# -*- coding: utf-8 -*-
{
    'name': "Secuencia para Código de Productos",
    'version': '1.0',
    'category' : 'Res Partner - Contacto',
    'license': 'Other proprietary',
    'summary': """Esta aplicación añade secuencial para la utilización del Producto.""",
    'author': "CorpoEureka",
    'website': "http://www.corpoeureka.com",
    'description': """
Se modifica el default code (referencia interna) para que sea secuencial y solo lectura
Tales como:
Secuencia
    """,
    'depends': [
                'base',
                'stock',
                'product',
                ],
    'data':[
       'data/code_sequence.xml',
       'views/product_template_view.xml',
    ],
    'installable' : True,
    'application' : False,
}