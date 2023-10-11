{

	'name':'Sales for the period',
    'version':'1.0',
    'category': 'Ventas',
    'author': 'CorpoEureka',
    'author': 'CorpoEureka',
    'support': 'proyectos@corpoeureka.com',
    'website' : 'http://www.corpoeureka.com',
    'license' : 'OPL-1',
    'description': """
    	Modulo para generar el total de ventas por periodo de fechas
    """,
    	
	'data':[
		'security/ir.model.access.csv',
		'views/sales_period_view.xml',
		'reports/sales_period_report.xml',
		'reports/sales_period_template.xml',
	],
	'depends':[
		'base',
		'account',
	]
}