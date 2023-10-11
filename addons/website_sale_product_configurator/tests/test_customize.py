# Part of Odoo. See LICENSE file for full copyright and licensing details.

<<<<<<< HEAD
from odoo.tests.common import HttpCase
=======
from odoo.tests.common import HttpSavepointCase
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
from odoo.addons.sale_product_configurator.tests.common import TestProductConfiguratorCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
<<<<<<< HEAD
class TestUi(HttpCase, TestProductConfiguratorCommon):

    def test_01_admin_shop_custom_attribute_value_tour(self):
        # Ensure that only one pricelist is available during the test, with the company currency.
        # This ensures that tours with triggers on the amounts will run properly.
        # To this purpose, we will ensure that only the public_pricelist is available for the default_website.
        public_pricelist = self.env.ref('product.list0')
        default_website = self.env.ref('website.default_website')
        self.env['product.pricelist'].search([
            ('id', '!=', public_pricelist.id),
            ('website_id', 'in', [False, default_website.id])]
        ).website_id = self.env.ref('website.website2')
        public_pricelist.currency_id = self.env.company.currency_id
        self._create_pricelist(public_pricelist)
=======
class TestUi(HttpSavepointCase, TestProductConfiguratorCommon):

    def test_01_admin_shop_custom_attribute_value_tour(self):
        # fix runbot, sometimes one pricelist is chosen, sometimes the other...
        pricelists = self.env['website'].get_current_website().get_current_pricelist() | self.env.ref('product.list0')
        self._create_pricelist(pricelists)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        self.start_tour("/", 'a_shop_custom_attribute_value', login="admin")
