{
    'name': "Codigo Alterno",

    'summary': """
        Agrega un campo en res.partner llamado codigo Alterno""",

    'description': """
        esta aplicacion, agrega un campo en la ficha del contacto llamado codigo alterno
    """,

    'author': "CorpoEureka",
    'website': "http://www.CorpoEureka.com",


    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail','contacts','account',
    ],

    # always loaded
    'data': [
        
        'views/inherited_sale_order.xml',
        'views/inherited_account_move.xml',

        
    ],
    # only loaded in demonstration mode
    'demo': [

        'demo/demo.xml',
    ],
}
