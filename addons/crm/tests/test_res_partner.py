# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

<<<<<<< HEAD
from odoo.addons.crm.tests.common import TestCrmCommon
from odoo.tests.common import Form
from odoo.tests import tagged, users


@tagged('res_partner')
class TestPartner(TestCrmCommon):

    @users('user_sales_leads')
    def test_parent_sync_sales_rep(self):
        """ Test team_id / user_id sync from parent to children if the contact
        is a person. Company children are not updated. """
        contact_company = self.contact_company.with_env(self.env)
        contact_company_1 = self.contact_company_1.with_env(self.env)
        self.assertFalse(contact_company.team_id)
        self.assertFalse(contact_company.user_id)
        self.assertFalse(contact_company_1.team_id)
        self.assertFalse(contact_company_1.user_id)

        child = self.contact_1.with_env(self.env)
        self.assertEqual(child.parent_id, self.contact_company_1)
        self.assertFalse(child.team_id)
        self.assertFalse(child.user_id)

        # update comppany sales rep info
        contact_company.user_id = self.env.uid
        contact_company.team_id = self.sales_team_1.id

        # change child parent: shold update sales rep info
        child.parent_id = contact_company.id
        self.assertEqual(child.user_id, self.env.user)

        # test form tool
        # <field name="team_id" groups="base.group_no_one"/>
        with self.debug_mode():
            partner_form = Form(self.env['res.partner'], 'base.view_partner_form')
        partner_form.parent_id = contact_company
        partner_form.company_type = 'person'
        partner_form.name = 'Hermes Conrad'
        self.assertEqual(partner_form.team_id, self.sales_team_1)
        self.assertEqual(partner_form.user_id, self.env.user)
        partner_form.parent_id = contact_company_1
        self.assertEqual(partner_form.team_id, self.sales_team_1)
        self.assertEqual(partner_form.user_id, self.env.user)

        # test form tool
        # <field name="team_id" groups="base.group_no_one"/>
        with self.debug_mode():
            partner_form = Form(self.env['res.partner'], 'base.view_partner_form')
        # `parent_id` is invisible when `is_company` is True (`company_type == 'company'`)
        # and parent_id is not set
        # So, set a temporary `parent_id` before setting the contact as company
        # to make `parent_id` visible in the interface while being a company
        # <field name="parent_id"
        #     attrs="{
        #         'invisible': [
        #             '|',
        #             '&amp;', ('is_company','=', True),('parent_id', '=', False),
        #             ('company_name', '!=', False),('company_name', '!=', '')
        #         ]
        #     }"
        # />
        partner_form.parent_id = contact_company_1
        partner_form.company_type = 'company'
        partner_form.parent_id = contact_company
        partner_form.name = 'Mom Corp'
        self.assertFalse(partner_form.team_id)
        self.assertFalse(partner_form.user_id)
=======
from odoo.tests.common import TransactionCase
from odoo.tests.common import new_test_user


class TestResPartner(TransactionCase):

    def test_meeting_count(self):
        test_user = new_test_user(self.env, login='test_user', groups='sales_team.group_sale_salesman')
        Partner = self.env['res.partner'].with_user(test_user)
        Event = self.env['calendar.event'].with_user(test_user)

        # Partner hierarchy
        #     1       5
        #    /|
        #   2 3
        #     |
        #     4

        test_partner_1 = Partner.create({'name': 'test_partner_1'})
        test_partner_2 = Partner.create({'name': 'test_partner_2', 'parent_id': test_partner_1.id})
        test_partner_3 = Partner.create({'name': 'test_partner_3', 'parent_id': test_partner_1.id})
        test_partner_4 = Partner.create({'name': 'test_partner_4', 'parent_id': test_partner_3.id})
        test_partner_5 = Partner.create({'name': 'test_partner_5'})

        Event.create({'name': 'event_1',
                      'partner_ids': [(6, 0, [test_partner_1.id,
                                              test_partner_2.id,
                                              test_partner_3.id,
                                              test_partner_4.id])]})
        Event.create({'name': 'event_2',
                      'partner_ids': [(6, 0, [test_partner_1.id,
                                              test_partner_3.id])]})
        Event.create({'name': 'event_2',
                      'partner_ids': [(6, 0, [test_partner_2.id,
                                              test_partner_3.id])]})
        Event.create({'name': 'event_3',
                      'partner_ids': [(6, 0, [test_partner_3.id,
                                              test_partner_4.id])]})
        Event.create({'name': 'event_4',
                      'partner_ids': [(6, 0, [test_partner_1.id])]})
        Event.create({'name': 'event_5',
                      'partner_ids': [(6, 0, [test_partner_3.id])]})
        Event.create({'name': 'event_6',
                      'partner_ids': [(6, 0, [test_partner_4.id])]})
        Event.create({'name': 'event_7',
                      'partner_ids': [(6, 0, [test_partner_5.id])]})
        Event.create({'name': 'event_8',
                      'partner_ids': [(6, 0, [test_partner_5.id])]})

        #Test rule to see if ir.rules are applied
        calendar_event_model_id = self.env['ir.model']._get('calendar.event').id
        self.env['ir.rule'].create({'name': 'test_rule',
                                    'model_id': calendar_event_model_id,
                                    'domain_force': [('name', 'not in', ['event_9', 'event_10'])],
                                    'perm_read': True,
                                    'perm_create': False,
                                    'perm_write': False})

        Event.create({'name': 'event_9',
                      'partner_ids': [(6, 0, [test_partner_2.id,
                                              test_partner_3.id])]})

        Event.create({'name': 'event_10',
                      'partner_ids': [(6, 0, [test_partner_5.id])]})

        self.assertEqual(test_partner_1.meeting_count, 7)
        self.assertEqual(test_partner_2.meeting_count, 2)
        self.assertEqual(test_partner_3.meeting_count, 6)
        self.assertEqual(test_partner_4.meeting_count, 3)
        self.assertEqual(test_partner_5.meeting_count, 2)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
