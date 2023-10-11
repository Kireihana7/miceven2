# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MailingContact(models.Model):
    _name = 'mailing.contact'
    _inherit = ['mailing.contact', 'mail.thread.phone']

    mobile = fields.Char(string='Mobile')

<<<<<<< HEAD
    def _phone_get_number_fields(self):
=======
    def _sms_get_number_fields(self):
        # TDE note: should override _phone_get_number_fields but ok as sms is in dependencies
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        return ['mobile']
