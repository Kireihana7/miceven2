# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tools import mute_logger
from odoo.tests import common, tagged


@tagged('mail_message')
<<<<<<< HEAD
class TestMessageFormatPortal(common.TransactionCase):
=======
class TestMessageFormatPortal(common.SavepointCase):
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    @mute_logger('odoo.models.unlink')
    def test_mail_message_format(self):
        """ Test the specific message formatting for the portal.
        Notably the flag that tells if the message is of subtype 'note'. """

        partner = self.env['res.partner'].create({'name': 'Partner'})
        message_no_subtype = self.env['mail.message'].create([{
            'model': 'res.partner',
            'res_id': partner.id,
        }])
        formatted_result = message_no_subtype.portal_message_format()
        # no defined subtype -> should return False
        self.assertFalse(formatted_result[0].get('is_message_subtype_note'))

        message_comment = self.env['mail.message'].create([{
            'model': 'res.partner',
            'res_id': partner.id,
<<<<<<< HEAD
            'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment'),
=======
            'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }])
        formatted_result = message_comment.portal_message_format()
        # subtype is a comment -> should return False
        self.assertFalse(formatted_result[0].get('is_message_subtype_note'))

        message_note = self.env['mail.message'].create([{
            'model': 'res.partner',
            'res_id': partner.id,
<<<<<<< HEAD
            'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
=======
            'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }])
        formatted_result = message_note.portal_message_format()
        # subtype is note -> should return True
        self.assertTrue(formatted_result[0].get('is_message_subtype_note'))
