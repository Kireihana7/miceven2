# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.tools import html2plaintext


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    def execute_command_lead(self, **kwargs):
        partner = self.env.user.partner_id
        key = kwargs['body']
        if key.strip() == '/lead':
            msg = _('Create a new lead (/lead lead title)')
        else:
            lead = self._convert_visitor_to_lead(partner, key)
            msg = _(
                'Created a new lead: %s',
                lead._get_html_link(),
            )
        self._send_transient_message(partner, msg)

<<<<<<< HEAD
    def _convert_visitor_to_lead(self, partner, key):
        """ Create a lead from channel /lead command
        :param partner: internal user partner (operator) that created the lead;
        :param key: operator input in chat ('/lead Lead about Product')
        """
=======
    def _convert_visitor_to_lead(self, partner, channel_partners, key):
        """ Create a lead from channel /lead command
        :param partner: internal user partner (operator) that created the lead;
        :param channel_partners: channel members;
        :param key: operator input in chat ('/lead Lead about Product')
        """
        description = ''.join(
            '%s: %s\n' % (message.author_id.name or self.anonymous_name, message.body)
            for message in self.channel_message_ids.sorted('id')
        )
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        # if public user is part of the chat: consider lead to be linked to an
        # anonymous user whatever the participants. Otherwise keep only share
        # partners (no user or portal user) to link to the lead.
        customers = self.env['res.partner']
<<<<<<< HEAD
        for customer in self.with_context(active_test=False).channel_partner_ids.filtered(lambda p: p != partner and p.partner_share):
            if customer.is_public:
=======
        for customer in channel_partners.partner_id.filtered('partner_share').with_context(active_test=False):
            if customer.user_ids and all(user._is_public() for user in customer.user_ids):
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                customers = self.env['res.partner']
                break
            else:
                customers |= customer

        utm_source = self.env.ref('crm_livechat.utm_source_livechat', raise_if_not_found=False)
        return self.env['crm.lead'].create({
            'name': html2plaintext(key[5:]),
            'partner_id': customers[0].id if customers else False,
            'user_id': False,
            'team_id': False,
<<<<<<< HEAD
            'description': self._get_channel_history(),
=======
            'description': html2plaintext(description),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            'referred': partner.name,
            'source_id': utm_source and utm_source.id,
        })
