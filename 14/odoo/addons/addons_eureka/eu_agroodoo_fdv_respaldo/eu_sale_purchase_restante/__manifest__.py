# -*- coding: utf-8 -*-

{
    'name': "Integration with Purchase and Sale Payment",
    'version': '1.1.4',
    'category' : 'Purchase',
    'license': 'Other proprietary',
    'summary': """This app allow you to select on Purchase.""",
    'author': "CorpoEureka",
    'website': "http://www.corpoeureka.com",
    'description': """
This app allow you to set Advance on Purchase.
Purchase Advance Smart Button
    """,
    'depends': [
                'purchase',
                'account',
                'purchase_payment',
                'sale_payment',
                'eu_multi_currency',
                ],
    'data':[
       'views/purchase_view.xml',
       'views/sale_view.xml',
    ],
    'installable' : True,
    'application' : False,
}
