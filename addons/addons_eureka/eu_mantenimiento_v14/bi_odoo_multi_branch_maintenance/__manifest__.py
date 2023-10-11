# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Maintenance Multiple Branch/Units Operations',
    'version': '14.0.0.1',
    'category': 'Extra Tools',
    'summary': 'Multiple Branch Management MRO Multi Branch Maintenance app Multiple Unit Operating unit Maintenance multi branch MRO operation multi branch Maintenance branch Maintenance repair management for single company with Multi Branches multi company',
    "description": """
       Multiple Unit operation management for single company, Mutiple Branch management for single company, multiple operation for single company.
    multiple Branch for Maintenance
    multiple Branch Operation for Maintenance,
    multiple unit operation on Maintenance management
    multiple unit operation for Maintenance management
    branch on Maintenance
    Branch on Maintenance management
    different unit on Maintenance
    Maintenance Unit Operation For single company
       branch Maintenance
       Maintenance branch
       Maintenance operating unit
       Maintenance unit operation management
      Maintenance multiple unit
       operating unit Maintenance
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    "price": 39.00,
    "currency": 'EUR',
    'depends': ['base','maintenance','hr_maintenance','purchase'],
    'data': [
                'security/maintenance_security.xml',
                'security/ir.model.access.csv',
                'views/maintenance_branch_view.xml',
             ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/sW6mMCdDdVQ',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
