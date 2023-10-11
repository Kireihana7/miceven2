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
    'depends': ['purchase','stock','sale_management','eu_multi_currency'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/views.xml',
    ],
    'qweb': [
        # 'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 69,
    'currency': 'EUR',
}
