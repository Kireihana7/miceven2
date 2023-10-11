# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Extended Addresses',
    'summary': 'Add extra fields on addresses',
    'sequence': '19',
    'version': '1.1',
    'category': 'Hidden',
    'description': """
Extended Addresses Management
=============================

This module provides the ability to choose a city from a list (in specific countries).

It is primarily used for EDIs that might need a special city code.
        """,
    'data': [
        'security/ir.model.access.csv',
        'views/base_address_extended.xml',
        'views/res_city_view.xml',
        'views/res_country_view.xml',
    ],
    'depends': ['base'],
<<<<<<< HEAD
=======
    'post_init_hook': '_update_street_format',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
