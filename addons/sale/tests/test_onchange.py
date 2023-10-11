# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestSaleOnchanges(TransactionCase):

    def test_sale_warnings(self):
        """Test warnings & SO/SOL updates when partner/products with sale warnings are used."""
        partner_with_warning = self.env['res.partner'].create({
            'name': 'Test', 'sale_warn': 'warning', 'sale_warn_msg': 'Highly infectious disease'})
        partner_with_block_warning = self.env['res.partner'].create({
            'name': 'Test2', 'sale_warn': 'block', 'sale_warn_msg': 'Cannot afford our services'})

<<<<<<< HEAD
        sale_order = self.env['sale.order'].create({'partner_id': partner_with_warning.id})
        warning = sale_order._onchange_partner_id_warning()
        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test",
                'message': partner_with_warning.sale_warn_msg,
            },
=======
    def test_onchange_product_id(self):

        uom_id = self.product_uom_model.search([('name', '=', 'Units')])[0]
        pricelist = self.pricelist_model.search([('name', '=', 'Public Pricelist')])[0]

        partner_id = self.res_partner_model.create(dict(name="George"))
        tax_include_id = self.tax_model.create(dict(name="Include tax",
                                                    amount='21.00',
                                                    price_include=True,
                                                    type_tax_use='sale'))
        tax_exclude_id = self.tax_model.create(dict(name="Exclude tax",
                                                    amount='0.00',
                                                    type_tax_use='sale'))

        product_tmpl_id = self.product_tmpl_model.create(dict(name="Voiture",
                                                              list_price=121,
                                                              taxes_id=[(6, 0, [tax_include_id.id])]))

        product_id = product_tmpl_id.product_variant_id

        fp_id = self.fiscal_position_model.create(dict(name="fiscal position", sequence=1))

        fp_tax_id = self.fiscal_position_tax_model.create(dict(position_id=fp_id.id,
                                                               tax_src_id=tax_include_id.id,
                                                               tax_dest_id=tax_exclude_id.id))

        # Create the SO with one SO line and apply a pricelist and fiscal position on it
        order_form = Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id = partner_id
        order_form.pricelist_id = pricelist
        order_form.fiscal_position_id = fp_id
        with order_form.order_line.new() as line:
            line.name = product_id.name
            line.product_id = product_id
            line.product_uom_qty = 1.0
            line.product_uom = uom_id
        sale_order = order_form.save()

        # Check the unit price of SO line
        self.assertEqual(100, sale_order.order_line[0].price_unit, "The included tax must be subtracted to the price")

    def test_fiscalposition_application(self):
        """Test application of a fiscal position mapping
        price included to price included tax
        """

        uom = self.product_uom_model.search([('name', '=', 'Units')])
        pricelist = self.pricelist_model.search([('name', '=', 'Public Pricelist')])

        partner = self.res_partner_model.create({
            'name': "George"
        })
        tax_fixed_incl = self.tax_model.create({
            'name': "fixed include",
            'amount': '10.00',
            'amount_type': 'fixed',
            'price_include': True,
        })
        tax_fixed_excl = self.tax_model.create({
            'name': "fixed exclude",
            'amount': '10.00',
            'amount_type': 'fixed',
            'price_include': False,
        })
        tax_include_src = self.tax_model.create({
            'name': "Include 21%",
            'amount': 21.00,
            'amount_type': 'percent',
            'price_include': True,
        })
        tax_include_dst = self.tax_model.create({
            'name': "Include 6%",
            'amount': 6.00,
            'amount_type': 'percent',
            'price_include': True,
        })
        tax_exclude_src = self.tax_model.create({
            'name': "Exclude 15%",
            'amount': 15.00,
            'amount_type': 'percent',
            'price_include': False,
        })
        tax_exclude_dst = self.tax_model.create({
            'name': "Exclude 21%",
            'amount': 21.00,
            'amount_type': 'percent',
            'price_include': False,
        })
        product_tmpl_a = self.product_tmpl_model.create({
            'name': "Voiture",
            'list_price': 121,
            'taxes_id': [(6, 0, [tax_include_src.id])]
        })

        product_tmpl_b = self.product_tmpl_model.create({
            'name': "Voiture",
            'list_price': 100,
            'taxes_id': [(6, 0, [tax_exclude_src.id])]
        })

        product_tmpl_c = self.product_tmpl_model.create({
            'name': "Voiture",
            'list_price': 100,
            'taxes_id': [(6, 0, [tax_fixed_incl.id, tax_exclude_src.id])]
        })

        product_tmpl_d = self.product_tmpl_model.create({
            'name': "Voiture",
            'list_price': 100,
            'taxes_id': [(6, 0, [tax_fixed_excl.id, tax_include_src.id])]
        })

        fpos_incl_incl = self.fiscal_position_model.create({
            'name': "incl -> incl",
            'sequence': 1
        })

        self.fiscal_position_tax_model.create({
            'position_id' :fpos_incl_incl.id,
            'tax_src_id': tax_include_src.id,
            'tax_dest_id': tax_include_dst.id
        })

        fpos_excl_incl = self.fiscal_position_model.create({
            'name': "excl -> incl",
            'sequence': 2,
        })

        self.fiscal_position_tax_model.create({
            'position_id' :fpos_excl_incl.id,
            'tax_src_id': tax_exclude_src.id,
            'tax_dest_id': tax_include_dst.id
        })

        fpos_incl_excl = self.fiscal_position_model.create({
            'name': "incl -> excl",
            'sequence': 3,
        })

        self.fiscal_position_tax_model.create({
            'position_id' :fpos_incl_excl.id,
            'tax_src_id': tax_include_src.id,
            'tax_dest_id': tax_exclude_dst.id
        })

        fpos_excl_excl = self.fiscal_position_model.create({
            'name': "excl -> excp",
            'sequence': 4,
        })

        self.fiscal_position_tax_model.create({
            'position_id' :fpos_excl_excl.id,
            'tax_src_id': tax_exclude_src.id,
            'tax_dest_id': tax_exclude_dst.id
        })

        # Create the SO with one SO line and apply a pricelist and fiscal position on it
        # Then check if price unit and price subtotal matches the expected values

        # Test Mapping included to included
        order_form = Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id = partner
        order_form.pricelist_id = pricelist
        order_form.fiscal_position_id = fpos_incl_incl
        with order_form.order_line.new() as line:
            line.name = product_tmpl_a.product_variant_id.name
            line.product_id = product_tmpl_a.product_variant_id
            line.product_uom_qty = 1.0
            line.product_uom = uom
        sale_order = order_form.save()
        self.assertRecordValues(sale_order.order_line, [{'price_unit': 106, 'price_subtotal': 100}])

        # Test Mapping excluded to included
        order_form = Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id = partner
        order_form.pricelist_id = pricelist
        order_form.fiscal_position_id = fpos_excl_incl
        with order_form.order_line.new() as line:
            line.name = product_tmpl_b.product_variant_id.name
            line.product_id = product_tmpl_b.product_variant_id
            line.product_uom_qty = 1.0
            line.product_uom = uom
        sale_order = order_form.save()
        self.assertRecordValues(sale_order.order_line, [{'price_unit': 100, 'price_subtotal': 94.34}])

        # Test Mapping included to excluded
        order_form = Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id = partner
        order_form.pricelist_id = pricelist
        order_form.fiscal_position_id = fpos_incl_excl
        with order_form.order_line.new() as line:
            line.name = product_tmpl_a.product_variant_id.name
            line.product_id = product_tmpl_a.product_variant_id
            line.product_uom_qty = 1.0
            line.product_uom = uom
        sale_order = order_form.save()
        self.assertRecordValues(sale_order.order_line, [{'price_unit': 100, 'price_subtotal': 100}])

        # Test Mapping excluded to excluded
        order_form = Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id = partner
        order_form.pricelist_id = pricelist
        order_form.fiscal_position_id = fpos_excl_excl
        with order_form.order_line.new() as line:
            line.name = product_tmpl_b.product_variant_id.name
            line.product_id = product_tmpl_b.product_variant_id
            line.product_uom_qty = 1.0
            line.product_uom = uom
        sale_order = order_form.save()
        self.assertRecordValues(sale_order.order_line, [{'price_unit': 100, 'price_subtotal': 100}])

        # Test Mapping (included,excluded) to (included, included)
        order_form = Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id = partner
        order_form.pricelist_id = pricelist
        order_form.fiscal_position_id = fpos_excl_incl
        with order_form.order_line.new() as line:
            line.name = product_tmpl_c.product_variant_id.name
            line.product_id = product_tmpl_c.product_variant_id
            line.product_uom_qty = 1.0
            line.product_uom = uom
        sale_order = order_form.save()
        self.assertRecordValues(sale_order.order_line, [{'price_unit': 100, 'price_subtotal': 84.91}])

        # Test Mapping (excluded,included) to (excluded, excluded)
        order_form = Form(self.env['sale.order'].with_context(tracking_disable=True))
        order_form.partner_id = partner
        order_form.pricelist_id = pricelist
        order_form.fiscal_position_id = fpos_incl_excl
        with order_form.order_line.new() as line:
            line.name = product_tmpl_d.product_variant_id.name
            line.product_id = product_tmpl_d.product_variant_id
            line.product_uom_qty = 1.0
            line.product_uom = uom
        sale_order = order_form.save()
        self.assertRecordValues(sale_order.order_line, [{'price_unit': 100, 'price_subtotal': 100}])

    def test_pricelist_application(self):
        """ Test different prices are correctly applied based on dates """
        support_product = self.env['product.product'].create({
            'name': 'Virtual Home Staging',
            'list_price': 100,
        })
        partner = self.res_partner_model.create(dict(name="George"))

        christmas_pricelist = self.env['product.pricelist'].create({
            'name': 'Christmas pricelist',
            'item_ids': [(0, 0, {
                'date_start': "2017-12-01",
                'date_end': "2017-12-24",
                'compute_price': 'percentage',
                'base': 'list_price',
                'percent_price': 20,
                'applied_on': '3_global',
                'name': 'Pre-Christmas discount'
            }), (0, 0, {
                'date_start': "2017-12-25",
                'date_end': "2017-12-31",
                'compute_price': 'percentage',
                'base': 'list_price',
                'percent_price': 50,
                'applied_on': '3_global',
                'name': 'Post-Christmas super-discount'
            })]
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        })

        sale_order.partner_id = partner_with_block_warning
        warning = sale_order._onchange_partner_id_warning()
        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test2",
                'message': partner_with_block_warning.sale_warn_msg,
            },
        })

        # Verify partner-related fields have been correctly reset
        self.assertFalse(sale_order.partner_id.id)
        self.assertFalse(sale_order.partner_invoice_id.id)
        self.assertFalse(sale_order.partner_shipping_id.id)
        self.assertFalse(sale_order.pricelist_id.id)

        # Reuse non blocking partner for product warning tests
        sale_order.partner_id = partner_with_warning
        product_with_warning = self.env['product.product'].create({
            'name': 'Test Product', 'sale_line_warn': 'warning', 'sale_line_warn_msg': 'Highly corrosive'})
        product_with_block_warning = self.env['product.product'].create({
            'name': 'Test Product (2)', 'sale_line_warn': 'block', 'sale_line_warn_msg': 'Not produced anymore'})

        sale_order_line = self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': product_with_warning.id,
        })
        warning = sale_order_line._onchange_product_id_warning()
        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test Product",
                'message': product_with_warning.sale_line_warn_msg,
            },
        })

        sale_order_line.product_id = product_with_block_warning
        warning = sale_order_line._onchange_product_id_warning()

        self.assertDictEqual(warning, {
            'warning': {
                'title': "Warning for Test Product (2)",
                'message': product_with_block_warning.sale_line_warn_msg,
            },
        })

        self.assertFalse(sale_order_line.product_id.id)
