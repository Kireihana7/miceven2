# -*- coding: utf-8 -*-
# purches Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

<<<<<<< HEAD
    def _action_send_mail(self, auto_commit=False):
        if self.model == 'purchase.order':
            self = self.with_context(mailing_document_based=True)
            if self.env.context.get('mark_rfq_as_sent'):
                self = self.with_context(mail_notify_author=self.env.user.partner_id in self.partner_ids)
        return super(MailComposeMessage, self)._action_send_mail(auto_commit=auto_commit)
=======
    def send_mail(self, auto_commit=False):
        if self.env.context.get('mark_rfq_as_sent') and self.model == 'purchase.order':
            self = self.with_context(mail_notify_author=self.env.user.partner_id in self.partner_ids)
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
