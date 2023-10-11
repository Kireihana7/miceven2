{
	
	'name': 'Informe de Objetivos de Ventas',
    'version': '13.0.1.0',
    'category': 'Ventas',
    'author': 'CorpoEureka',
    'website': 'http://www.corpoeureka.com', 
    'description': """
       Este modulo muestra las metas por cumplir de cada vendedor
    """,

	'data':[
		'security/ir.model.access.csv',
		'views/sales_target_wizard_view.xml',
		'reports/sales_target_report.xml',
		'reports/sales_target_templates.xml',
	],
	'depends':[
		'base',
		'sale_management',
		'salesperson_sales_target_app',
	]
}