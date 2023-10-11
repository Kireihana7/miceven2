{
    'name': 'Base import',
    'description': """
New extensible file import for Odoo
======================================

Re-implement Odoo's file import system:

* Server side, the previous system forces most of the logic into the
  client which duplicates the effort (between clients), makes the
  import system much harder to use without a client (direct RPC or
  other forms of automation) and makes knowledge about the
  import/export system much harder to gather as it is spread over
  3+ different projects.

* In a more extensible manner, so users and partners can build their
  own front-end to import from other file formats (e.g. OpenDocument
  files) which may be simpler to handle in their work flow or from
  their data production sources.

* In a module, so that administrators and users of Odoo who do not
  need or want an online import can avoid it being available to users.
""",
    'depends': ['web'],
    'version': '2.0',
    'category': 'Hidden/Tools',
    'installable': True,
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
    ],
<<<<<<< HEAD
    'assets': {
        'web.assets_backend': [
            'base_import/static/lib/javascript-state-machine/state-machine.js',
            'base_import/static/src/**/*.scss',
            'base_import/static/src/**/*.js',
            'base_import/static/src/**/*.xml',
        ],
        'web.qunit_suite_tests': [
            'base_import/static/tests/**/*',
        ],
    },
=======
    'qweb': ['static/src/xml/base_import.xml'],
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
