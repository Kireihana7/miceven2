{

	'name':'Sales by products',
    'version':'1.0',
    'category': 'Ventas',
    'author': 'CorpoEureka',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'license' : 'OPL-1',
    'description': """
    	Modulo para generar reporte de ventas por productos
    """,
    	
	'data':[
		'security/ir.model.access.csv',
		'views/sales_by_products_view.xml',
		'reports/sales_by_products_report.xml',
		'reports/sales_by_products_template.xml',
	],
	'depends':[
		'base',
		'account',
	]
}