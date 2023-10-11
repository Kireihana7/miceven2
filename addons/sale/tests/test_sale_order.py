# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import timedelta
from freezegun import freeze_time

from odoo import fields
from odoo.fields import Command
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged, Form
from odoo.tools import float_compare

from odoo.addons.sale.tests.common import SaleCommon


@tagged('post_install', '-at_install')
class TestSaleOrder(SaleCommon):

    # Those tests do not rely on accounting common on purpose
    #   If you need the accounting setup, use other classes (TestSaleToInvoice probably)

<<<<<<< HEAD
    def test_computes_auto_fill(self):
        free_product, dummy_product = self.env['product.product'].create([{
            'name': 'Free product',
            'list_price': 0.0,
        }, {
            'name': 'Dummy product',
            'list_price': 0.0,
        }])
        # Test pre-computes of lines with order
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'display_type': 'line_section',
                    'name': 'Dummy section',
                }),
                Command.create({
                    'display_type': 'line_section',
                    'name': 'Dummy section',
                }),
                Command.create({
                    'product_id': free_product.id,
                }),
                Command.create({
                    'product_id': dummy_product.id,
                })
            ]
        })

        # Test pre-computes of lines creation alone
        # Ensures the creation works fine even if the computes
        # are triggered after the defaults
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        self.env['sale.order.line'].create([
            {
                'display_type': 'line_section',
                'name': 'Dummy section',
                'order_id': order.id,
            }, {
                'display_type': 'line_section',
                'name': 'Dummy section',
                'order_id': order.id,
            }, {
                'product_id': free_product.id,
                'order_id': order.id,
            }, {
                'product_id': dummy_product.id,
                'order_id': order.id,
            }
        ])
=======
        SaleOrder = cls.env['sale.order'].with_context(tracking_disable=True)

        # set up users
        cls.crm_team0 = cls.env['crm.team'].create({
            'name': 'crm team 0',
            'company_id': cls.company_data['company'].id
        })
        cls.crm_team1 = cls.env['crm.team'].create({
            'name': 'crm team 1',
            'company_id': cls.company_data['company'].id
        })
        cls.user_in_team = cls.env['res.users'].create({
            'email': 'team0user@example.com',
            'login': 'team0user',
            'name': 'User in Team 0',
            'sale_team_id': cls.crm_team0.id
        })
        cls.user_not_in_team = cls.env['res.users'].create({
            'email': 'noteamuser@example.com',
            'login': 'noteamuser',
            'name': 'User Not In Team',
        })

        # create a generic Sale Order with all classical products and empty pricelist
        cls.sale_order = SaleOrder.create({
            'partner_id': cls.partner_a.id,
            'partner_invoice_id': cls.partner_a.id,
            'partner_shipping_id': cls.partner_a.id,
            'pricelist_id': cls.company_data['default_pricelist'].id,
        })
        cls.sol_product_order = cls.env['sale.order.line'].create({
            'name': cls.company_data['product_order_no'].name,
            'product_id': cls.company_data['product_order_no'].id,
            'product_uom_qty': 2,
            'product_uom': cls.company_data['product_order_no'].uom_id.id,
            'price_unit': cls.company_data['product_order_no'].list_price,
            'order_id': cls.sale_order.id,
            'tax_id': False,
        })
        cls.sol_serv_deliver = cls.env['sale.order.line'].create({
            'name': cls.company_data['product_service_delivery'].name,
            'product_id': cls.company_data['product_service_delivery'].id,
            'product_uom_qty': 2,
            'product_uom': cls.company_data['product_service_delivery'].uom_id.id,
            'price_unit': cls.company_data['product_service_delivery'].list_price,
            'order_id': cls.sale_order.id,
            'tax_id': False,
        })
        cls.sol_serv_order = cls.env['sale.order.line'].create({
            'name': cls.company_data['product_service_order'].name,
            'product_id': cls.company_data['product_service_order'].id,
            'product_uom_qty': 2,
            'product_uom': cls.company_data['product_service_order'].uom_id.id,
            'price_unit': cls.company_data['product_service_order'].list_price,
            'order_id': cls.sale_order.id,
            'tax_id': False,
        })
        cls.sol_product_deliver = cls.env['sale.order.line'].create({
            'name': cls.company_data['product_delivery_no'].name,
            'product_id': cls.company_data['product_delivery_no'].id,
            'product_uom_qty': 2,
            'product_uom': cls.company_data['product_delivery_no'].uom_id.id,
            'price_unit': cls.company_data['product_delivery_no'].list_price,
            'order_id': cls.sale_order.id,
            'tax_id': False,
        })

    def test_sale_order(self):
        """ Test the sales order flow (invoicing and quantity updates)
            - Invoice repeatedly while varrying delivered quantities and check that invoice are always what we expect
        """
        # TODO?: validate invoice and register payments
        self.sale_order.order_line.read(['name', 'price_unit', 'product_uom_qty', 'price_total'])
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    def test_sale_order_standard_flow(self):
        self.assertEqual(self.sale_order.amount_total, 725.0, 'Sale: total amount is wrong')
        self.sale_order.order_line._compute_product_updatable()
        self.assertTrue(self.sale_order.order_line[0].product_updatable)

        # send quotation
        email_act = self.sale_order.action_quotation_send()
        email_ctx = email_act.get('context', {})
        self.sale_order.with_context(**email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        self.assertTrue(self.sale_order.state == 'sent', 'Sale: state after sending is wrong')
        self.sale_order.order_line._compute_product_updatable()
        self.assertTrue(self.sale_order.order_line[0].product_updatable)

        # confirm quotation
        self.sale_order.action_confirm()
        self.assertTrue(self.sale_order.state == 'sale')
        self.assertTrue(self.sale_order.invoice_status == 'to invoice')

    def test_sale_order_send_to_self(self):
        # when sender(logged in user) is also present in recipients of the mail composer,
        # user should receive mail.
        sale_order = self.env['sale.order'].with_user(self.sale_user).create({
            'partner_id': self.sale_user.partner_id.id,
        })
        email_ctx = sale_order.action_quotation_send().get('context', {})
        # We need to prevent auto mail deletion, and so we copy the template and send the mail with
        # added configuration in copied template. It will allow us to check whether mail is being
        # sent to to author or not (in case author is present in 'Recipients' of composer).
        mail_template = self.env['mail.template'].browse(email_ctx.get('default_template_id')).copy({'auto_delete': False})
        # send the mail with same user as customer
        sale_order.with_context(**email_ctx).with_user(self.sale_user).message_post_with_template(mail_template.id)
        self.assertTrue(sale_order.state == 'sent', 'Sale : state should be changed to sent')
        mail_message = sale_order.message_ids[0]
        self.assertEqual(mail_message.author_id, sale_order.partner_id, 'Sale: author should be same as customer')
        self.assertEqual(mail_message.author_id, mail_message.partner_ids, 'Sale: author should be in composer recipients thanks to "partner_to" field set on template')
        self.assertEqual(mail_message.partner_ids, mail_message.sudo().mail_ids.recipient_ids, 'Sale: author should receive mail due to presence in composer recipients')

    def test_invoice_state_when_ordered_quantity_is_negative(self):
        """When you invoice a SO line with a product that is invoiced on ordered quantities and has negative ordered quantity,
        this test ensures that the  invoicing status of the SO line is 'invoiced' (and not 'upselling')."""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': -1,
            })]
        })
        sale_order.action_confirm()
        sale_order._create_invoices(final=True)
        self.assertTrue(sale_order.invoice_status == 'invoiced', 'Sale: The invoicing status of the SO should be "invoiced"')

    def test_sale_order_send_to_self(self):
        # when sender(logged in user) is also present in recipients of the mail composer,
        # user should receive mail.
        sale_order = self.env['sale.order'].with_user(self.company_data['default_user_salesman']).create({
            'partner_id': self.company_data['default_user_salesman'].partner_id.id,
            'order_line': [[0, 0, {
                'name':  self.company_data['product_order_no'].name,
                'product_id': self.company_data['product_order_no'].id,
                'product_uom_qty': 1,
                'price_unit': self.company_data['product_order_no'].list_price,
            }]]
        })
        email_ctx = sale_order.action_quotation_send().get('context', {})
        # We need to prevent auto mail deletion, and so we copy the template and send the mail with
        # added configuration in copied template. It will allow us to check whether mail is being
        # sent to to author or not (in case author is present in 'Recipients' of composer).
        mail_template = self.env['mail.template'].browse(email_ctx.get('default_template_id')).copy({'auto_delete': False})
        # send the mail with same user as customer
        sale_order.with_context(**email_ctx).with_user(self.company_data['default_user_salesman']).message_post_with_template(mail_template.id)
        self.assertTrue(sale_order.state == 'sent', 'Sale : state should be changed to sent')
        mail_message = sale_order.message_ids[0]
        self.assertEqual(mail_message.author_id, sale_order.partner_id, 'Sale: author should be same as customer')
        self.assertEqual(mail_message.author_id, mail_message.partner_ids, 'Sale: author should be in composer recipients thanks to "partner_to" field set on template')
        self.assertEqual(mail_message.partner_ids, mail_message.sudo().mail_ids.recipient_ids, 'Sale: author should receive mail due to presence in composer recipients')

    def test_invoice_state_when_ordered_quantity_is_negative(self):
        """When you invoice a SO line with a product that is invoiced on ordered quantities and has negative ordered quantity,
        this test ensures that the  invoicing status of the SO line is 'invoiced' (and not 'upselling')."""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [(0, 0, {
                'product_id': self.company_data['product_order_no'].id,
                'product_uom_qty': -1,
            })]
        })
        sale_order.action_confirm()
        sale_order._create_invoices(final=True)
        self.assertTrue(sale_order.invoice_status == 'invoiced', 'Sale: The invoicing status of the SO should be "invoiced"')

    def test_sale_sequence(self):
        self.env['ir.sequence'].search([
            ('code', '=', 'sale.order'),
        ]).write({
            'use_date_range': True, 'prefix': 'SO/%(range_year)s/',
        })
        sale_order = self.sale_order.copy({'date_order': '2019-01-01'})
        self.assertTrue(sale_order.name.startswith('SO/2019/'))
        sale_order = self.sale_order.copy({'date_order': '2020-01-01'})
        self.assertTrue(sale_order.name.startswith('SO/2020/'))
        # In EU/BXL tz, this is actually already 01/01/2020
        sale_order = self.sale_order.with_context(tz='Europe/Brussels').copy({'date_order': '2019-12-31 23:30:00'})
        self.assertTrue(sale_order.name.startswith('SO/2020/'))

    def test_unlink_cancel(self):
        """ Test deleting and cancelling sales orders depending on their state and on the user's rights """
        # SO in state 'draft' can be deleted
        so_copy = self.sale_order.copy()
        with self.assertRaises(AccessError):
            so_copy.with_user(self.sale_user).unlink()
        self.assertTrue(so_copy.unlink(), 'Sale: deleting a quotation should be possible')

        # SO in state 'cancel' can be deleted
        so_copy = self.sale_order.copy()
        so_copy.action_confirm()
        self.assertTrue(so_copy.state == 'sale', 'Sale: SO should be in state "sale"')
        so_copy._action_cancel()
        self.assertTrue(so_copy.state == 'cancel', 'Sale: SO should be in state "cancel"')
        with self.assertRaises(AccessError):
            so_copy.with_user(self.sale_user).unlink()
        self.assertTrue(so_copy.unlink(), 'Sale: deleting a cancelled SO should be possible')

        # SO in state 'sale' or 'done' cannot be deleted
        self.sale_order.action_confirm()
        self.assertTrue(self.sale_order.state == 'sale', 'Sale: SO should be in state "sale"')
        with self.assertRaises(UserError):
            self.sale_order.unlink()

        self.sale_order.action_done()
        self.assertTrue(self.sale_order.state == 'done', 'Sale: SO should be in state "done"')
        with self.assertRaises(UserError):
            self.sale_order.unlink()

    def test_onchange_packaging_00(self):
        """Create a SO and use packaging. Check we suggested suitable packaging
        according to the product_qty. Also check product_qty or product_packaging
        are correctly calculated when one of them changed.
        """
        # Required for `product_packaging_qty` to be visible in the view
        self.env.user.groups_id += self.env.ref('product.group_stock_packaging')
        packaging_single, packaging_dozen = self.env['product.packaging'].create([{
            'name': "I'm a packaging",
            'product_id': self.product.id,
            'qty': 1.0,
        }, {
            'name': "I'm also a packaging",
            'product_id': self.product.id,
            'qty': 12.0,
        }])

<<<<<<< HEAD
        so = self.empty_order
        so_form = Form(so)
        with so_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1.0
        so_form.save()
        self.assertEqual(so.order_line.product_packaging_id, packaging_single)
        self.assertEqual(so.order_line.product_packaging_qty, 1.0)
        with so_form.order_line.edit(0) as line:
            line.product_packaging_qty = 2.0
        so_form.save()
        self.assertEqual(so.order_line.product_uom_qty, 2.0)

        with so_form.order_line.edit(0) as line:
            line.product_uom_qty = 24.0
        so_form.save()
        self.assertEqual(so.order_line.product_packaging_id, packaging_dozen)
        self.assertEqual(so.order_line.product_packaging_qty, 2.0)
        with so_form.order_line.edit(0) as line:
            line.product_packaging_qty = 1.0
        so_form.save()
        self.assertEqual(so.order_line.product_uom_qty, 12)

        packaging_pack_of_10 = self.env['product.packaging'].create({
            'name': "PackOf10",
            'product_id': self.product.id,
            'qty': 10.0,
        })
        packaging_pack_of_20 = self.env['product.packaging'].create({
            'name': "PackOf20",
            'product_id': self.product.id,
            'qty': 20.0,
        })

        so2 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        so2_form = Form(so2)
        with so2_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 10
        so2_form.save()
        self.assertEqual(so2.order_line.product_packaging_id.id, packaging_pack_of_10.id)
        self.assertEqual(so2.order_line.product_packaging_qty, 1.0)

        with so2_form.order_line.edit(0) as line:
            line.product_packaging_qty = 2
        so2_form.save()
        self.assertEqual(so2.order_line.product_uom_qty, 20)
        # we should have 2 pack of 10, as we've set the package_qty manually,
        # we shouldn't recompute the packaging_id, since the package_qty is protected,
        # therefor cannot be recomputed during the same transaction, which could lead
        # to an incorrect line like (qty=20,pack_qty=2,pack_id=PackOf20)
        self.assertEqual(so2.order_line.product_packaging_qty, 2)
        self.assertEqual(so2.order_line.product_packaging_id.id, packaging_pack_of_10.id)

        with so2_form.order_line.edit(0) as line:
            line.product_packaging_id = packaging_pack_of_20
        so2_form.save()
        self.assertEqual(so2.order_line.product_uom_qty, 20)
        # we should have 1 pack of 20, as we've set the package type manually
        self.assertEqual(so2.order_line.product_packaging_qty, 1)
        self.assertEqual(so2.order_line.product_packaging_id.id, packaging_pack_of_20.id)

    def _create_sale_order(self):
        """Create dummy sale order (without lines)"""
        return self.env['sale.order'].with_context(
            default_sale_order_template_id=False
            # Do not modify test behavior even if sale_management is installed
        ).create({
            'partner_id': self.partner.id,
        })

    def test_invoicing_terms(self):
        # Enable invoicing terms
        self.env['ir.config_parameter'].sudo().set_param('account.use_invoice_terms', True)

        # Plain invoice terms
        self.env.company.terms_type = 'plain'
        self.env.company.invoice_terms = "Coin coin"
        sale_order = self._create_sale_order()
        self.assertEqual(sale_order.note, "<p>Coin coin</p>")

        # Html invoice terms (/terms page)
        self.env.company.terms_type = 'html'
        sale_order = self._create_sale_order()
        self.assertTrue(sale_order.note.startswith("<p>Terms &amp; Conditions: "))

    def test_validity_days(self):
        self.env['ir.config_parameter'].sudo().set_param('sale.use_quotation_validity_days', True)
        self.env.company.quotation_validity_days = 5
        with freeze_time("2020-05-02"):
            sale_order = self._create_sale_order()

            self.assertEqual(sale_order.validity_date, fields.Date.today() + timedelta(days=5))
        self.env.company.quotation_validity_days = 0
        sale_order = self._create_sale_order()
        self.assertFalse(
            sale_order.validity_date,
            "No validity date must be specified if the company validity duration is 0")

    def test_so_names(self):
        """Test custom context key for name_get & name_search.

        Note: this key is used in sale_expense & sale_timesheet modules.
        """
        SaleOrder = self.env['sale.order'].with_context(sale_show_partner_name=True)

        res = SaleOrder.name_search(name=self.sale_order.partner_id.name)
        self.assertEqual(res[0][0], self.sale_order.id)

        self.assertNotIn(self.sale_order.partner_id.name, self.sale_order.display_name)
        self.assertIn(
            self.sale_order.partner_id.name,
            self.sale_order.with_context(sale_show_partner_name=True).name_get()[0][1])

    def test_state_changes(self):
        """Test some untested state changes methods & logic."""
        self.sale_order.action_quotation_sent()

        self.assertEqual(self.sale_order.state, 'sent')
        self.assertIn(self.sale_order.partner_id, self.sale_order.message_follower_ids.partner_id)

        self.env.user.groups_id += self.env.ref('sale.group_auto_done_setting')
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, 'done', "The order wasn't automatically locked at confirmation.")
        with self.assertRaises(UserError):
            self.sale_order.action_confirm()

        self.sale_order.action_unlock()
        self.assertEqual(self.sale_order.state, 'sale')

    def test_sol_name_search(self):
        # Shouldn't raise
        self.env['sale.order']._search([('order_line', 'ilike', 'product')])

        name_search_data = self.env['sale.order.line'].name_search(name=self.sale_order.name)
        sol_ids_found = dict(name_search_data).keys()
        self.assertEqual(list(sol_ids_found), self.sale_order.order_line.ids)

    def test_zero_quantity(self):
        """
            If the quantity set is 0 it should remain to 0
            Test that changing the uom do not change the quantity
        """
        order_line = self.sale_order.order_line[0]
        order_line.product_uom_qty = 0.0
        order_line.product_uom = self.uom_dozen
        self.assertEqual(order_line.product_uom_qty, 0.0)

    def test_discount_rounding(self):
        """
            Check the discount is properly rounded and the price subtotal
            computed with this rounded discount
        """
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 192,
                'discount': 74.246,
            })]
        })
        self.assertEqual(sale_order.order_line.price_subtotal, 49.44, "Subtotal should be equal to 192 * (1 - 0.7425)")
        self.assertEqual(sale_order.order_line.discount, 74.25)

    def test_tax_amount_rounding(self):
        """ Check order amounts are rounded according to settings """

        tax_a = self.env['account.tax'].create({
            'name': 'Test tax',
            'type_tax_use': 'sale',
            'price_include': False,
            'amount_type': 'percent',
            'amount': 15.0,
        })

        # Test Round per Line (default)
        self.env.company.tax_calculation_rounding_method = 'round_per_line'
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 6.7,
                    'discount': 0,
                    'tax_id': tax_a.ids,
                }),
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 6.7,
                    'discount': 0,
                    'tax_id': tax_a.ids,
=======
        inv = self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'partner_id': self.partner_a.id,
            'invoice_date': so.date_order,
            'invoice_line_ids': [
                (0, 0, {
                    'name': serv_cost.name,
                    'product_id': serv_cost.id,
                    'product_uom_id': serv_cost.uom_id.id,
                    'quantity': 2,
                    'price_unit': serv_cost.standard_price,
                    'analytic_account_id': so.analytic_account_id.id,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                }),
            ],
        })
        self.assertEqual(sale_order.amount_total, 15.42, "")

        # Test Round Globally
        self.env.company.tax_calculation_rounding_method = 'round_globally'
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 6.7,
                    'discount': 0,
                    'tax_id': tax_a.ids,
                }),
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 6.7,
                    'discount': 0,
                    'tax_id': tax_a.ids,
                }),
            ],
        })
        self.assertEqual(sale_order.amount_total, 15.41, "")


@tagged('post_install', '-at_install')
class TestSalesTeam(SaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # set up users
        cls.sale_team_2 = cls.env['crm.team'].create({
            'name': 'Test Sales Team (2)',
        })
        cls.user_in_team = cls.env['res.users'].create({
            'email': 'team0user@example.com',
            'login': 'team0user',
            'name': 'User in Team 0',
        })
        cls.sale_team.write({'member_ids': [4, cls.user_in_team.id]})
        cls.user_not_in_team = cls.env['res.users'].create({
            'email': 'noteamuser@example.com',
            'login': 'noteamuser',
            'name': 'User Not In Team',
        })

    def test_assign_sales_team_from_partner_user(self):
        """Use the team from the customer's sales person, if it is set"""
        partner = self.env['res.partner'].create({
            'name': 'Customer of User In Team',
            'user_id': self.user_in_team.id,
            'team_id': self.sale_team_2.id,
        })
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
        })
        self.assertEqual(sale_order.team_id.id, self.sale_team.id, 'Should assign to team of sales person')

    def test_assign_sales_team_from_partner_team(self):
        """If no team set on the customer's sales person, fall back to the customer's team"""
        partner = self.env['res.partner'].create({
            'name': 'Customer of User Not In Team',
            'user_id': self.user_not_in_team.id,
            'team_id': self.sale_team_2.id,
        })
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
        })
        self.assertEqual(sale_order.team_id.id, self.sale_team_2.id, 'Should assign to team of partner')

    def test_assign_sales_team_when_changing_user(self):
        """When we assign a sales person, change the team on the sales order to their team"""
        sale_order = self.env['sale.order'].create({
            'user_id': self.user_not_in_team.id,
            'partner_id': self.partner.id,
            'team_id': self.sale_team_2.id
        })
        sale_order.user_id = self.user_in_team
        self.assertEqual(sale_order.team_id.id, self.sale_team.id, 'Should assign to team of sales person')

    def test_keep_sales_team_when_changing_user_with_no_team(self):
        """When we assign a sales person that has no team, do not reset the team to default"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'team_id': self.sale_team_2.id
        })
        sale_order.user_id = self.user_not_in_team
        self.assertEqual(sale_order.team_id.id, self.sale_team_2.id, 'Should not reset the team to default')

    def test_sale_order_analytic_distribution_change(self):
        self.env.user.groups_id += self.env.ref('analytic.group_analytic_accounting')

        analytic_plan = self.env['account.analytic.plan'].create({'name': 'Plan Test', 'company_id': False})
        analytic_account_super = self.env['account.analytic.account'].create({'name': 'Super Account', 'plan_id': analytic_plan.id})
        analytic_account_great = self.env['account.analytic.account'].create({'name': 'Great Account', 'plan_id': analytic_plan.id})
        super_product = self.env['product.product'].create({'name': 'Super Product'})
        great_product = self.env['product.product'].create({'name': 'Great Product'})
        product_no_account = self.env['product.product'].create({'name': 'Product No Account'})
        self.env['account.analytic.distribution.model'].create([
            {
                'analytic_distribution': {analytic_account_super.id: 100},
                'product_id': super_product.id,
            },
            {
                'analytic_distribution': {analytic_account_great.id: 100},
                'product_id': great_product.id,
            },
        ])
        sale_order = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })
        sol = self.env['sale.order.line'].create({
            'name': super_product.name,
            'product_id': super_product.id,
            'order_id': sale_order.id,
        })

        self.assertEqual(sol.analytic_distribution, {str(analytic_account_super.id): 100}, "The analytic distribution should be set to Super Account")
        sol.write({'product_id': great_product.id})
        self.assertEqual(sol.analytic_distribution, {str(analytic_account_great.id): 100}, "The analytic distribution should be set to Great Account")

        so_no_analytic_account = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })
        sol_no_analytic_account = self.env['sale.order.line'].create({
            'name': super_product.name,
            'product_id': super_product.id,
            'order_id': so_no_analytic_account.id,
            'analytic_distribution': False,
        })
        so_no_analytic_account.action_confirm()
        self.assertFalse(sol_no_analytic_account.analytic_distribution, "The compute should not overwrite what the user has set.")

        sale_order.action_confirm()
        sol_on_confirmed_order = self.env['sale.order.line'].create({
            'name': super_product.name,
            'product_id': super_product.id,
            'order_id': sale_order.id,
        })

        self.assertEqual(
            sol_on_confirmed_order.analytic_distribution,
            {str(analytic_account_super.id): 100},
            "The analytic distribution should be set to Super Account, even for confirmed orders"
        )


    def test_cannot_assign_tax_of_mismatch_company(self):
        """ Test that sol cannot have assigned tax belonging to a different company from that of the sale order. """
        company_a = self.env['res.company'].create({'name': 'A'})
        company_b = self.env['res.company'].create({'name': 'B'})

        tax_a = self.env['account.tax'].create({
            'name': 'A',
            'amount': 10,
            'company_id': company_a.id,
        })
        tax_b = self.env['account.tax'].create({
            'name': 'B',
            'amount': 10,
            'company_id': company_b.id,
        })

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'company_id': company_a.id
        })
        product = self.env['product.product'].create({'name': 'Product'})

        # In sudo to simulate an user that have access to both companies.
        sol = self.env['sale.order.line'].sudo().create({
            'name': product.name,
            'product_id': product.id,
            'order_id': sale_order.id,
            'tax_id': tax_a,
        })

<<<<<<< HEAD
        with self.assertRaises(UserError):
            sol.tax_id = tax_b
=======
        so_1 = self.env['sale.order'].with_user(self.company_data['default_user_salesman']).create({
            'partner_id': self.env['res.partner'].create({'name': 'A partner'}).id,
            'company_id': self.company_data['company'].id,
        })
        so_1.write({
            'order_line': [(0, False, {'product_id': product_shared.product_variant_id.id, 'order_id': so_1.id})],
        })

        self.assertEqual(so_1.order_line.tax_id, self.company_data['default_tax_sale'],
            'Only taxes from the right company are put by default')
        so_1.action_confirm()
        # i'm not interested in groups/acls, but in the multi-company flow only
        # the sudo is there for that and does not impact the invoice that gets created
        # the goal here is to invoice in company 1 (because the order is in company 1) while being
        # 'mainly' in company 2 (through the context), the invoice should be in company 1
        inv=so_1.sudo()\
            .with_context(allowed_company_ids=(self.company_data['company'] + self.company_data_2['company']).ids)\
            ._create_invoices()
        self.assertEqual(inv.company_id, self.company_data['company'], 'invoices should be created in the company of the SO, not the main company of the context')

    def test_group_invoice(self):
        """ Test that invoicing multiple sales order for the same customer works. """
        # Create 3 SOs for the same partner, one of which that uses another currency
        eur_pricelist = self.env['product.pricelist'].create({'name': 'EUR', 'currency_id': self.env.ref('base.EUR').id})
        so1 = self.sale_order.with_context(mail_notrack=True).copy()
        so1.pricelist_id = eur_pricelist
        so2 = so1.copy()
        usd_pricelist = self.env['product.pricelist'].create({'name': 'USD', 'currency_id': self.env.ref('base.USD').id})
        so3 = so1.copy()
        so1.pricelist_id = usd_pricelist
        orders = so1 | so2 | so3
        orders.action_confirm()
        # Create the invoicing wizard and invoice all of them at once
        wiz = self.env['sale.advance.payment.inv'].with_context(active_ids=orders.ids, open_invoices=True).create({})
        res = wiz.create_invoices()
        # Check that exactly 2 invoices are generated
        self.assertEqual(len(res['domain'][0][2]),2, "Grouping invoicing 3 orders for the same partner with 2 currencies should create exactly 2 invoices")

    def test_so_note_to_invoice(self):
        """Test that notes from SO are pushed into invoices"""

        sol_note = self.env['sale.order.line'].create({
            'name': 'This is a note',
            'display_type': 'line_note',
            'product_id': False,
            'product_uom_qty': 0,
            'product_uom': False,
            'price_unit': 0,
            'order_id': self.sale_order.id,
            'tax_id': False,
        })

        # confirm quotation
        self.sale_order.action_confirm()

        # create invoice
        invoice = self.sale_order._create_invoices()

        # check note from SO has been pushed in invoice
        self.assertEqual(len(invoice.invoice_line_ids.filtered(lambda line: line.display_type == 'line_note')), 1, 'Note SO line should have been pushed to the invoice')

    def test_multi_currency_discount(self):
        """Verify the currency used for pricelist price & discount computation."""
        products = self.env["product.product"].search([], limit=2)
        product_1 = products[0]
        product_2 = products[1]

        # Make sure the company is in USD
        main_company = self.env.ref('base.main_company')
        main_curr = main_company.currency_id
        current_curr = self.env.company.currency_id
        other_curr = self.currency_data['currency']
        # main_company.currency_id = other_curr # product.currency_id when no company_id set
        other_company = self.env["res.company"].create({
            "name": "Test",
            "currency_id": other_curr.id
        })
        user_in_other_company = self.env["res.users"].create({
            "company_id": other_company.id,
            "company_ids": [(6, 0, [other_company.id])],
            "name": "E.T",
            "login": "hohoho",
        })
        user_in_other_company.groups_id |= self.env.ref('product.group_discount_per_so_line')
        self.env['res.currency.rate'].search([]).unlink()
        self.env['res.currency.rate'].create({
            'name': '2010-01-01',
            'rate': 2.0,
            'currency_id': main_curr.id,
            "company_id": False,
        })

        product_1.company_id = False
        product_2.company_id = False

        self.assertEqual(product_1.currency_id, main_curr)
        self.assertEqual(product_2.currency_id, main_curr)
        self.assertEqual(product_1.cost_currency_id, current_curr)
        self.assertEqual(product_2.cost_currency_id, current_curr)

        product_1_ctxt = product_1.with_user(user_in_other_company)
        product_2_ctxt = product_2.with_user(user_in_other_company)
        self.assertEqual(product_1_ctxt.currency_id, main_curr)
        self.assertEqual(product_2_ctxt.currency_id, main_curr)
        self.assertEqual(product_1_ctxt.cost_currency_id, other_curr)
        self.assertEqual(product_2_ctxt.cost_currency_id, other_curr)

        product_1.lst_price = 100.0
        product_2_ctxt.standard_price = 10.0 # cost is company_dependent

        pricelist = self.env["product.pricelist"].create({
            "name": "Test multi-currency",
            "discount_policy": "without_discount",
            "currency_id": other_curr.id,
            "item_ids": [
                (0, 0, {
                    "base": "list_price",
                    "product_id": product_1.id,
                    "compute_price": "percentage",
                    "percent_price": 20,
                }),
                (0, 0, {
                    "base": "standard_price",
                    "product_id": product_2.id,
                    "compute_price": "percentage",
                    "percent_price": 10,
                })
            ]
        })

        # Create a SO in the other company
        ##################################
        # product_currency = main_company.currency_id when no company_id on the product

        # CASE 1:
        # company currency = so currency
        # product_1.currency != so currency
        # product_2.cost_currency_id = so currency
        sales_order = product_1_ctxt.with_context(mail_notrack=True, mail_create_nolog=True).env["sale.order"].create({
            "partner_id": self.env.user.partner_id.id,
            "pricelist_id": pricelist.id,
            "order_line": [
                (0, 0, {
                    "product_id": product_1.id,
                    "product_uom_qty": 1.0
                }),
                (0, 0, {
                    "product_id": product_2.id,
                    "product_uom_qty": 1.0
                })
            ]
        })
        for line in sales_order.order_line:
            # Create values autofill does not compute discount.
            line._onchange_discount()

        so_line_1 = sales_order.order_line[0]
        so_line_2 = sales_order.order_line[1]
        self.assertEqual(so_line_1.discount, 20)
        self.assertEqual(so_line_1.price_unit, 50.0)
        self.assertEqual(so_line_2.discount, 10)
        self.assertEqual(so_line_2.price_unit, 10)

        # CASE 2
        # company currency != so currency
        # product_1.currency == so currency
        # product_2.cost_currency_id != so currency
        pricelist.currency_id = main_curr
        sales_order = product_1_ctxt.with_context(mail_notrack=True, mail_create_nolog=True).env["sale.order"].create({
            "partner_id": self.env.user.partner_id.id,
            "pricelist_id": pricelist.id,
            "order_line": [
                # Verify discount is considered in create hack
                (0, 0, {
                    "product_id": product_1.id,
                    "product_uom_qty": 1.0
                }),
                (0, 0, {
                    "product_id": product_2.id,
                    "product_uom_qty": 1.0
                })
            ]
        })
        for line in sales_order.order_line:
            line._onchange_discount()

        so_line_1 = sales_order.order_line[0]
        so_line_2 = sales_order.order_line[1]
        self.assertEqual(so_line_1.discount, 20)
        self.assertEqual(so_line_1.price_unit, 100.0)
        self.assertEqual(so_line_2.discount, 10)
        self.assertEqual(so_line_2.price_unit, 20)

    def test_assign_sales_team_from_partner_user(self):
        """Use the team from the customer's sales person, if it is set"""
        partner = self.env['res.partner'].create({
            'name': 'Customer of User In Team',
            'user_id': self.user_in_team.id,
            'team_id': self.crm_team1.id,
        })
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
        })
        sale_order.onchange_partner_id()
        self.assertEqual(sale_order.team_id.id, self.crm_team0.id, 'Should assign to team of sales person')

    def test_assign_sales_team_from_partner_team(self):
        """If no team set on the customer's sales person, fall back to the customer's team"""
        partner = self.env['res.partner'].create({
            'name': 'Customer of User Not In Team',
            'user_id': self.user_not_in_team.id,
            'team_id': self.crm_team1.id,
        })
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
        })
        sale_order.onchange_partner_id()
        self.assertEqual(sale_order.team_id.id, self.crm_team1.id, 'Should assign to team of partner')

    def test_assign_sales_team_when_changing_user(self):
        """When we assign a sales person, change the team on the sales order to their team"""
        sale_order = self.env['sale.order'].create({
            'user_id': self.user_not_in_team.id,
            'partner_id': self.partner_a.id,
            'team_id': self.crm_team1.id
        })
        sale_order.user_id = self.user_in_team
        sale_order.onchange_user_id()
        self.assertEqual(sale_order.team_id.id, self.crm_team0.id, 'Should assign to team of sales person')

    def test_keep_sales_team_when_changing_user_with_no_team(self):
        """When we assign a sales person that has no team, do not reset the team to default"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'team_id': self.crm_team1.id
        })
        sale_order.user_id = self.user_not_in_team
        sale_order.onchange_user_id()
        self.assertEqual(sale_order.team_id.id, self.crm_team1.id, 'Should not reset the team to default')

    def test_discount_and_untaxed_subtotal(self):
        """When adding a discount on a SO line, this test ensures that the untaxed amount to invoice is
        equal to the untaxed subtotal"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [(0, 0, {
                'product_id': self.product_a.id,
                'product_uom_qty': 38,
                'price_unit': 541.26,
                'discount': 2.00,
            })]
        })
        sale_order.action_confirm()
        line = sale_order.order_line
        self.assertEqual(line.untaxed_amount_to_invoice, 0)

        line.qty_delivered = 38
        # (541.26 - 0.02 * 541.26) * 38 = 20156.5224 ~= 20156.52
        self.assertEqual(line.price_subtotal, 20156.52)
        self.assertEqual(line.untaxed_amount_to_invoice, line.price_subtotal)

        # Same with an included-in-price tax
        sale_order = sale_order.copy()
        line = sale_order.order_line
        line.tax_id = [(0, 0, {
            'name': 'Super Tax',
            'amount_type': 'percent',
            'amount': 15.0,
            'price_include': True,
        })]
        sale_order.action_confirm()
        self.assertEqual(line.untaxed_amount_to_invoice, 0)

        line.qty_delivered = 38
        # (541,26 / 1,15) * ,98 * 38 = 17527,410782609 ~= 17527.41
        self.assertEqual(line.price_subtotal, 17527.41)
        self.assertEqual(line.untaxed_amount_to_invoice, line.price_subtotal)

    def test_discount_and_amount_undiscounted(self):
        """When adding a discount on a SO line, this test ensures that amount undiscounted is
        consistent with the used tax"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [(0, 0, {
                'product_id': self.product_a.id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
                'discount': 1.00,
            })]
        })
        sale_order.action_confirm()
        line = sale_order.order_line

        # test discount and qty 1
        self.assertEqual(sale_order.amount_undiscounted, 100.0)
        self.assertEqual(line.price_subtotal, 99.0)

        # more quantity 1 -> 3
        sale_form = Form(sale_order)
        with sale_form.order_line.edit(0) as line_form:
            line_form.product_uom_qty = 3.0
            line_form.price_unit = 100.0
        sale_order = sale_form.save()

        self.assertEqual(sale_order.amount_undiscounted, 300.0)
        self.assertEqual(line.price_subtotal, 297.0)

        # undiscounted
        with sale_form.order_line.edit(0) as line_form:
            line_form.discount = 0.0
        sale_order = sale_form.save()
        self.assertEqual(line.price_subtotal, 300.0)
        self.assertEqual(sale_order.amount_undiscounted, 300.0)

        # Same with an included-in-price tax
        sale_order = sale_order.copy()
        line = sale_order.order_line
        line.tax_id = [(0, 0, {
            'name': 'Super Tax',
            'amount_type': 'percent',
            'amount': 10.0,
            'price_include': True,
        })]
        line.discount = 50.0
        sale_order.action_confirm()

        # 300 with 10% incl tax -> 272.72 total tax excluded without discount
        # 136.36 price tax excluded with discount applied
        self.assertEqual(sale_order.amount_undiscounted, 272.72)
        self.assertEqual(line.price_subtotal, 136.36)

    def test_free_product_and_price_include_fixed_tax(self):
        """ Check that fixed tax include are correctly computed while the price_unit is 0
        """
        # please ensure this test remains consistent with
        # test_out_invoice_line_onchange_2_taxes_fixed_price_include_free_product in account module
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [(0, 0, {
                'product_id': self.company_data['product_order_no'].id,
                'product_uom_qty': 1,
                'price_unit': 0.0,
            })]
        })
        sale_order.action_confirm()
        line = sale_order.order_line
        line.tax_id = [
            (0, 0, {
                'name': 'BEBAT 0.05',
                'type_tax_use': 'sale',
                'amount_type': 'fixed',
                'amount': 0.05,
                'price_include': True,
                'include_base_amount': True,
            }),
            (0, 0, {
                'name': 'Recupel 0.25',
                'type_tax_use': 'sale',
                'amount_type': 'fixed',
                'amount': 0.25,
                'price_include': True,
                'include_base_amount': True,
            }),
        ]
        sale_order.action_confirm()
        self.assertRecordValues(sale_order, [{
            'amount_untaxed': -0.30,
            'amount_tax': 0.30,
            'amount_total': 0.0,
        }])

    def test_sol_name_search(self):
        # Shouldn't raise
        self.env['sale.order']._search([('order_line', 'ilike', 'acoustic')])

        name_search_data = self.env['sale.order.line'].name_search(name=self.sale_order.name)
        sol_ids_found = dict(name_search_data).keys()
        self.assertEqual(list(sol_ids_found), self.sale_order.order_line.ids)

    def test_sale_order_analytic_tag_change(self):
        self.env.user.groups_id += self.env.ref('analytic.group_analytic_accounting')
        self.env.user.groups_id += self.env.ref('analytic.group_analytic_tags')

        analytic_account_super = self.env['account.analytic.account'].create({'name': 'Super Account'})
        analytic_account_great = self.env['account.analytic.account'].create({'name': 'Great Account'})
        analytic_tag_super = self.env['account.analytic.tag'].create({'name': 'Super Tag'})
        analytic_tag_great = self.env['account.analytic.tag'].create({'name': 'Great Tag'})
        super_product = self.env['product.product'].create({'name': 'Super Product'})
        great_product = self.env['product.product'].create({'name': 'Great Product'})
        product_no_account = self.env['product.product'].create({'name': 'Product No Account'})
        self.env['account.analytic.default'].create([
            {
                'analytic_id': analytic_account_super.id,
                'product_id': super_product.id,
                'analytic_tag_ids': [analytic_tag_super.id],
            },
            {
                'analytic_id': analytic_account_great.id,
                'product_id': great_product.id,
                'analytic_tag_ids': [analytic_tag_great.id],
            },
        ])
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
        })
        sol = self.env['sale.order.line'].create({
            'name': super_product.name,
            'product_id': super_product.id,
            'order_id': sale_order.id,
        })

        self.assertEqual(sol.analytic_tag_ids.id, analytic_tag_super.id, "The analytic tag should be set to 'Super Tag'")
        sol.write({'product_id': great_product.id})
        self.assertEqual(sol.analytic_tag_ids.id, analytic_tag_great.id, "The analytic tag should be set to 'Great Tag'")
        sol.write({'product_id': product_no_account.id})
        self.assertFalse(sol.analytic_tag_ids.id, "The analytic account should not be set")

        so_no_analytic_account = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
        })
        sol_no_analytic_account = self.env['sale.order.line'].create({
            'name': super_product.name,
            'product_id': super_product.id,
            'order_id': so_no_analytic_account.id,
            'analytic_tag_ids': False,
        })
        so_no_analytic_account.action_confirm()
        self.assertFalse(sol_no_analytic_account.analytic_tag_ids.id, "The compute should not overwrite what the user has set.")
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
