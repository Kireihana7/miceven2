# -*- coding: utf-8 -*-
{
    'name' : 'Reporte y alerta de expiración en Producto',
    'version': '14.0.0.1',
    'category': 'Sale',
    'description': """
Reporte y alerta de expiración en producto
    """,
    'depends': ['base', 'sale_management', 'stock','sale_stock', 'purchase',
                 'account', 'product_expiry'],
    'data': [
        'views/res_config_setting.xml',
        'views/product_expiry_config_view.xml',
        'views/product_expiry_report_view.xml',
        'views/view_production_lot.xml',
        'report/grp_category_product_expiry_report_template.xml',
        'report/report.xml',
        'data/mail_template.xml',
        'data/product_expiry_scheduler.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv'


    ],
    'qweb': [
                'static/src/xml/*.xml',
        'static/src/xml/expiry_dashboard/dashboard.xml',
    ],
    'installable': True,
}