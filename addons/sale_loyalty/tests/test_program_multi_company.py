# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

<<<<<<< HEAD:addons/sale_loyalty/tests/test_program_multi_company.py
from odoo.addons.sale_loyalty.tests.common import TestSaleCouponCommon
=======
from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/sale_coupon/tests/test_program_multi_company.py
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestSaleCouponMultiCompany(TestSaleCouponCommon):

    def setUp(self):
        super(TestSaleCouponMultiCompany, self).setUp()

        self.company_a = self.env.company
        self.company_b = self.env['res.company'].create(dict(name="TEST"))

<<<<<<< HEAD:addons/sale_loyalty/tests/test_program_multi_company.py
        self.immediate_promotion_program_c2 = self.env['loyalty.program'].create({
            'name': 'Buy A + 1 B, 1 B are free',
            'trigger': 'auto',
            'program_type': 'promotion',
            'applies_on': 'current',
            'company_id': self.company_b.id,
            'rule_ids': [(0, 0, {
                'product_ids': self.product_A,
                'reward_point_amount': 1,
                'reward_point_mode': 'order',
            })],
            'reward_ids': [(0, 0, {
                'reward_type': 'product',
                'reward_product_id': self.product_B.id,
                'reward_product_qty': 1,
                'required_points': 1,
            })],
        })

    def _get_applicable_programs(self, order):
        return self.env['loyalty.program'].browse(p.id for p in order._get_applicable_program_points())

=======
        self.immediate_promotion_program_c2 = self.env['coupon.program'].create({
            'name': 'Buy A + 1 B, 1 B are free',
            'promo_code_usage': 'no_code_needed',
            'reward_type': 'product',
            'reward_product_id': self.product_B.id,
            'rule_products_domain': "[('id', 'in', [%s])]" % (self.product_A.id),
            'active': True,
            'company_id': self.company_b.id,
        })

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/sale_coupon/tests/test_program_multi_company.py
    def test_applicable_programs(self):

        order = self.empty_order
        order.write({'order_line': [
            (0, False, {
                'product_id': self.product_A.id,
                'name': '1 Product A',
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
            }),
            (0, False, {
                'product_id': self.product_B.id,
                'name': '2 Product B',
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
            })
        ]})
<<<<<<< HEAD:addons/sale_loyalty/tests/test_program_multi_company.py
        order._update_programs_and_rewards()

        self.assertNotIn(self.immediate_promotion_program_c2, self._get_applicable_programs(order))
        self.assertNotIn(self.immediate_promotion_program_c2, order._get_applied_programs())
=======
        order.recompute_coupon_lines()

        def _get_applied_programs(order):
            # temporary copy of sale_order._get_applied_programs
            # to ensure each commit stays independent
            # can be later removed and replaced in master.
            return order.code_promo_program_id + order.no_code_promo_program_ids + order.applied_coupon_ids.mapped('program_id')

        self.assertNotIn(self.immediate_promotion_program_c2, order._get_applicable_programs())
        self.assertNotIn(self.immediate_promotion_program_c2, _get_applied_programs(order))
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/sale_coupon/tests/test_program_multi_company.py

        order_b = self.env["sale.order"].create({
            'company_id': self.company_b.id,
            'partner_id': order.partner_id.id,
        })
        order_b.write({'order_line': [
            (0, False, {
                'product_id': self.product_A.id,
                'name': '1 Product A',
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
            }),
            (0, False, {
                'product_id': self.product_B.id,
                'name': '2 Product B',
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
            })
        ]})
<<<<<<< HEAD:addons/sale_loyalty/tests/test_program_multi_company.py
        self.assertNotIn(self.immediate_promotion_program, self._get_applicable_programs(order_b))
        order_b._update_programs_and_rewards()
        self.assertIn(self.immediate_promotion_program_c2, order_b._get_applied_programs())
        self.assertNotIn(self.immediate_promotion_program, order_b._get_applied_programs())
=======
        self.assertNotIn(self.immediate_promotion_program, order_b._get_applicable_programs())

        order_b.recompute_coupon_lines()
        self.assertIn(self.immediate_promotion_program_c2, _get_applied_programs(order_b))
        self.assertNotIn(self.immediate_promotion_program, _get_applied_programs(order_b))
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/sale_coupon/tests/test_program_multi_company.py
