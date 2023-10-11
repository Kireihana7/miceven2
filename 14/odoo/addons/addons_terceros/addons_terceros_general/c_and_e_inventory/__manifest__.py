{
    'name': 'Create and edit restriction for Inventory',
    'version': '14.0.2',
    'description': """This module consists, the product creating and editing restriction in 
                   Inventory""",
    'category': 'Inventory',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['stock','stock_landed_costs','purchase_stock','mrp_landed_costs','product'],
    'data': [   
        'views/inventory_restriction.xml',   
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
