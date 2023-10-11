# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Multiple Branch Unit Operation for Fleet/Vehicle App',
    'version': '14.0.0.1',
    'category': 'Fleet',
    'summary': 'Multiple Branch fleet Multi Branch Multiple Operating unit for fleet multi branch fleet branch fleet multi branch unit branch vehicle fleet management for single company with Multi Branches multi company vehicle branch vehicle branch with fleet management',
    "description": """
        This app for mutiple branch management for single company, multiple branch operation on fleet management.
       
        multiple Branch for fleet in odoo,
        multiple Branch Operation for fleet in odoo,
        multiple unit operation on fleet management,
        multiple unit operation for vehical management in odoo,
        branch on fleet vehical in odoo,
        Branch on vehical fleet management in odoo,
        different unit on fleet on odoo,
        fleet Unit Operation For single company in odoo,

       """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    "price": 30,
    "currency": 'EUR',
    'depends': ['base','fleet','branch'],
    'data': [
                'security/fleet_security.xml',
                'security/ir.model.access.csv',
                'views/fleet_branch_view.xml',
             ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/9r4RgFlnRiI',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
