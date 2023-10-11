{    
    'name': 'Nuevo Reporte de ordenes de Compras',
    'version': '1.0',
    'category': 'Purchase',
    'author': 'CorpoEureka',
    'website': 'http://www.corpoeureka.com',
    'description': """
       Nuevo reporte de orden de compra personalizado
    """,
    'depends':[
    	'purchase',
        'stock',
    ],
    'data':[
        'views/purchase_order_templates.xml',
    	'views/purchase_reports.xml',
    	'views/purchase_order_view.xml',
    ],
    'installable': True,
}