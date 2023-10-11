# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Presence Control',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """
Control Employees Presence
==========================

Based on:
    * The IP Address
    * The User's Session
    * The Sent Emails

Allows to contact directly the employee in case of unjustified absence.
    """,
    'depends': ['hr', 'hr_holidays', 'sms'],
    'data': [
        'security/sms_security.xml',
        'security/ir.model.access.csv',
        'data/ir_actions_server.xml',
        'views/hr_employee_views.xml',
        'data/mail_template_data.xml',
        'data/sms_data.xml',
<<<<<<< HEAD
=======
        'data/mail_data.xml',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        'data/ir_cron.xml',
    ],
    'installable': True,
<<<<<<< HEAD
    'post_init_hook': 'post_init_hook',
=======
    'auto_install': False,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
