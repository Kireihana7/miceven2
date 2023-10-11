{

	'name':'Sales Order Line Limit',
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
		'security/groups.xml',
		'views/res_company_view.xml',
	],
	'depends':[
		'base',
		'sale',
	]
}