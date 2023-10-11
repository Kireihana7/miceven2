odoo.define('website_sale_wishlist_admin.tour', function (require) {
'use strict';

<<<<<<< HEAD
const wTourUtils = require("website.tour_utils");

wTourUtils.registerWebsitePreviewTour('shop_wishlist_admin', {
    url: '/shop?search=Rock',
    test: true,
},
    [
        {
            content: "Go to Rock shop page",
            trigger: 'iframe a:contains("Rock"):first',
        },
        {
            content: "check list view of variants is disabled initially (when on /product page)",
            trigger: 'iframe body:not(:has(.js_product_change))',
            extra_trigger: 'iframe #product_details',
        },
        ...wTourUtils.clickOnEditAndWaitEditMode(),
        {
            content: "open customize tab",
            trigger: '.o_we_customize_snippet_btn',
        },
        {
            content: "open 'Variants' selector",
            extra_trigger: '#oe_snippets .o_we_customize_panel',
            trigger: '[data-name="variants_opt"] we-toggler',
        },
        {
            content: "click on 'List View of Variants'",
            trigger: 'we-button[data-name="variants_products_list_opt"]',
        },
        ...wTourUtils.clickOnSave(),
        {
            content: "check page loaded after list of variant customization enabled",
            trigger: 'iframe .js_product_change',
        },
        {
            content: "Add red product in wishlist",
            trigger: 'iframe #product_detail .o_add_wishlist_dyn:not(".disabled")',
        },
        {
            content: "Check that wishlist contains 1 items",
            trigger: 'iframe .my_wish_quantity:contains(1)',
            run: function () {
                window.location.href = '/@/shop/wishlist';
=======
var rpc = require('web.rpc');
var tour = require("web_tour.tour");

tour.register('shop_wishlist_admin', {
    test: true,
    url: '/shop',
},
    [
        {
            content: "Create a product with always attribute and its values.",
            trigger: 'body',
            run: function () {
                rpc.query({
                    model: 'product.attribute',
                    method: 'create',
                    args: [{
                        'name': "color",
                        'display_type': 'color',
                        'create_variant': 'always'
                    }],
                }).then(function (attributeId) {
                    return rpc.query({
                        model: 'product.template',
                        method: 'create',
                        args: [{
                            'name': "Rock",
                            'is_published': true,
                            'attribute_line_ids': [[0, 0, {
                                'attribute_id': attributeId,
                                'value_ids': [
                                    [0, 0, {
                                        'name': "red",
                                        'attribute_id': attributeId,
                                    }],
                                    [0, 0, {
                                        'name': "blue",
                                        'attribute_id': attributeId,
                                    }],
                                    [0, 0, {
                                        'name': "black",
                                        'attribute_id': attributeId,
                                    }],
                                ]
                            }]],
                        }],
                    });
                }).then(function () {
                    window.location.href = '/shop?search=Rock';
                });
            },
        },
        {
            content: "Go to Rock shop page",
            trigger: 'a:contains("Rock"):first',
        },
        {
            content: "check list view of variants is disabled initially (when on /product page)",
            trigger: 'body:not(:has(.js_product_change))',
            extra_trigger: '#product_details',
        },
        {
            content: "open customize menu",
            trigger: '#customize-menu > a',
            extra_trigger: 'body:not(.notReady)',
        },
        {
            content: "click on 'List View of Variants'",
            trigger: '#customize-menu a:contains(List View of Variants)',
        },
        {
            content: "check page loaded after list of variant customization enabled",
            trigger: '.js_product_change',
        },
        {
            content: "Add red product in wishlist",
            trigger: '#product_detail .o_add_wishlist_dyn:not(".disabled")',
        },
        {
            content: "Check that wishlist contains 1 items",
            extra_trigger : '#product_detail .o_add_wishlist_dyn:disabled',
            trigger: '.my_wish_quantity:contains(1)',
            run: function () {
                window.location.href = '/shop/wishlist';
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
        },
        {
            content: "Check wishlist contains first variant",
<<<<<<< HEAD
            trigger: 'iframe #o_comparelist_table tr:contains("red")',
            run: function () {
                window.location.href = '/@/shop?search=Rock';
=======
            trigger: '#o_comparelist_table tr:contains("red")',
            run: function () {
                window.location.href = '/shop?search=Rock';
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
        },
        {
            content: "Go to Rock shop page",
<<<<<<< HEAD
            trigger: 'iframe a:contains("Rock"):first',
        },
        {
            content: "Switch to black Rock",
            trigger: 'iframe .js_product span:contains("black")',
        },
        {
            content: "Add black rock to wishlist",
            trigger: 'iframe #product_detail .o_add_wishlist_dyn:not(".disabled")',
        },
        {
            content: "Check that black product was added",
            trigger: 'iframe .my_wish_quantity:contains(2)',
            run: function () {
                window.location.href = '/@/shop/wishlist';
=======
            trigger: 'a:contains("Rock"):first',
        },
        {
            content: "Switch to black Rock",
            trigger: '.js_product span:contains("black")',
        },
        {
            content: "Switch to black Rock",
            trigger: '#product_detail .o_add_wishlist_dyn:not(".disabled")',
        },
        {
            content: "Check that black product was added",
            extra_trigger : '#product_detail .o_add_wishlist_dyn:disabled',
            trigger: '.my_wish_quantity:contains(2)',
            run: function () {
                window.location.href = '/shop/wishlist';
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
        },
        {
            content: "Check wishlist contains both variants",
<<<<<<< HEAD
            extra_trigger: 'iframe #o_comparelist_table tr:contains("red")',
            trigger: 'iframe #o_comparelist_table tr:contains("black")',
            run: function () {}, // This is a check
=======
            extra_trigger: '#o_comparelist_table tr:contains("red")',
            trigger: '#o_comparelist_table tr:contains("black")',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        },
    ]
);

});
