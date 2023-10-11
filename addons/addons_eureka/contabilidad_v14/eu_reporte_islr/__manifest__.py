{
	'name':'Reporte ISLR',
	'descripion':'Modulo para generar reporte Impuesto Sobre la Renta por Conceptos',
	'data':[
		'security/ir.model.access.csv',
		'views/islr_wizard_view.xml',
		'reports/islr_report.xml',
		'reports/islr_templates.xml',
	],
	'depends':[
		'base',
		'account',
		'l10n_ve_retencion_islr',
	]
}