# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

<<<<<<< HEAD
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestName(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_name = 'Product Test Name'
        cls.product_code = 'PTN'
        cls.product = cls.env['product.product'].create({
            'name': cls.product_name,
            'default_code': cls.product_code,
=======
from odoo.tests.common import TransactionCase


class TestName(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product_name = 'Product Test Name'
        self.product_code = 'PTN'
        self.product = self.env['product.product'].create({
            'name': self.product_name,
            'default_code': self.product_code,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        })

    def test_10_product_name(self):
        display_name = self.product.display_name
        self.assertEqual(display_name, "[%s] %s" % (self.product_code, self.product_name),
<<<<<<< HEAD
                         "Code should be preprended the name as the context is not preventing it.")
=======
                         "Code should be preprended the the name as the context is not preventing it.")
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        display_name = self.product.with_context(display_default_code=False).display_name
        self.assertEqual(display_name, self.product_name,
                         "Code should not be preprended to the name as context should prevent it.")

    def test_default_code_and_negative_operator(self):
        res = self.env['product.template'].name_search(name='PTN', operator='not ilike')
        res_ids = [r[0] for r in res]
        self.assertNotIn(self.product.id, res_ids)
