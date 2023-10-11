# -*- coding: utf-8 -*-
{
    'name': 'test-translation-import',
    'version': '0.1',
    'category': 'Hidden/Tests',
    'description': """A module to test translation import.""",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'view.xml',
        'data/test_translation_import_data.xml'
    ],
    'installable': True,
<<<<<<< HEAD
    'assets': {
        'web.assets_backend': [
            'test_translation_import/static/src/xml/js_templates.xml',
        ],
    },
=======
    'auto_install': False,
    'qweb': [
        'static/src/xml/js_templates.xml',
    ],
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
