{
    'name': "Zona de Contactos",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        esta aplicacion, mustra la zona de los contactos
    """,

    'author': "CorpoEureka",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail','contacts','branch',
    ],

    # always loaded
    'data': [
        
        'security/ir.model.access.csv',
        'views/zone_contacts_view.xml',
        'views/zone_contacts_inherit_view.xml',
        'views/inherited_sale_order_zone.xml',
        'views/zone_invoice_inherit_view.xml',
        
        
    ],
    # only loaded in demonstration mode
    'demo': [

        'demo/demo.xml',
    ],
}
