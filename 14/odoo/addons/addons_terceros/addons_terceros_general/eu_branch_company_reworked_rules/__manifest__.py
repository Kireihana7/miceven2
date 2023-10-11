#-*- coding:utf-8 -*-

{
    'name': 'Add multi-company to branch',
    'category': '',
    'summary': 'Add multi-company to branch rules',
    'description': "",
    'depends': [
        'branch',
    ],
    'data': [
        'data/branch_rules.xml',
        'data/search_groups.xml',
    ],
    'installable': True,
    'application': True,
}
