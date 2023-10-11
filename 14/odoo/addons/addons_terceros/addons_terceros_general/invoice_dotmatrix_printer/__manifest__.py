# -*- coding: utf-8 -*-
#Modulo de : ErpMstar Solutions
#modificado por Corpoeureka
#Desarrolador : Elio Meza eliomeza1@gmail.com

{
    'name': 'Account Invoice Dotmatrix Printer',
    'version': '1.0',
    'category': 'Sale',
    'sequence': 6,
    'author': 'ErpMstar Solutions',
    'summary': 'Le permite imprimir Facturas, Notas de entrega, Débito, Credito, Ficha de Pesaje de Romana mediante una impresora matricial.',
    'description': "Allows you to print Account Invoice, Tranfer Stock, Gestion de Romana report by dot matrix printer.",
    'depends': ['purchase','stock','sale_management','eu_agroindustry','eu_aliv_maisa_invoice'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
    ],
    'qweb': [
        # 'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/receipt.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 30,
    'currency': 'EUR',
}
