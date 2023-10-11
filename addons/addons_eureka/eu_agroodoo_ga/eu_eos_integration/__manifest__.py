# -*- coding: utf-8 -*-
{
    'name': "eu_eos_integration",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    "sequence": -299,
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/default_datasets_abbreviation.xml',
        'data/default_datasets.xml',
        'views/menu.xml',
        'views/eos_feature_views.xml',
        'views/eos_statistics_views.xml',
        'views/eos_download_views.xml',
        'views/eos_field_views.xml',
        'views/eos_zoning_views.xml',
        'views/eos_datasets_views.xml',
        'views/eos_datasets_abbreviation_views.xml',
        # 'views/res_config_settings_views.xml',        
        'views/res_config_settings_views.xml',
    ],
}
