# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Skills e-learning',
    'category': 'Hidden',
    'version': '1.0',
    'summary': 'Add completed courses to resume of your employees',
    'description':
        """
E-learning and Skills for HR
============================

This module add completed courses to resume for employees.
        """,
    'depends': ['hr_skills', 'website_slides'],
    'data': [
        'views/hr_employee_views.xml',
        'views/hr_templates.xml',
        'data/hr_resume_data.xml',
    ],
    'auto_install': True,
<<<<<<< HEAD
    'assets': {
        'web.assets_backend': [
            'hr_skills_slides/static/src/scss/**/*',
            'hr_skills_slides/static/src/xml/**/*',
        ],
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
