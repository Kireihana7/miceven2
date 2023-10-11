odoo.define('website_sale.s_dynamic_snippet_products_options', function (require) {
'use strict';

const options = require('web_editor.snippets.options');
const s_dynamic_snippet_carousel_options = require('website.s_dynamic_snippet_carousel_options');

var wUtils = require('website.utils');

const alternativeSnippetRemovedOptions = [
    'filter_opt', 'product_category_opt', 'product_tag_opt', 'product_names_opt',
]

const dynamicSnippetProductsOptions = s_dynamic_snippet_carousel_options.extend({

    /**
     *
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.modelNameFilter = 'product.product';
        // Directly calling $() will not work in this case since we are querying something
        // in an iframe
        const productTemplateId = this.$target.closest("#wrapwrap").find("input.product_template_id");
        this.hasProductTemplateId = productTemplateId.val();
        if (!this.hasProductTemplateId) {
            this.contextualFilterDomain.push(['product_cross_selling', '=', false]);
        }
        this.productCategories = {};
        this.isAlternativeProductSnippet = this.$target.hasClass('o_wsale_alternative_products');
    },
    /**
     * @override
     */
    onBuilt() {
        this._super.apply(this, arguments);
        // TODO Remove in master.
        this.$target[0].dataset['snippet'] = 's_dynamic_snippet_products';
<<<<<<< HEAD
=======
        this._rpc({
            route: '/website_sale/snippet/options_filters'
        }).then((data) => {
            if (data.length) {
                this.$target.get(0).dataset.filterId = data[0].id;
                this.$target.get(0).dataset.numberOfRecords = this.dynamicFilters[data[0].id].limit;
                this._refreshPublicWidgets();
                // Refresh is needed because default values are obtained after start()
            }
        });
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @override
     */
     _computeWidgetVisibility(widgetName, params) {
        if (this.isAlternativeProductSnippet && alternativeSnippetRemovedOptions.includes(widgetName)) {
            return false;
        }
        return this._super(...arguments);
    },
    /**
     * Fetches product categories.
     * @private
     * @returns {Promise}
     */
    _fetchProductCategories: function () {
        return this._rpc({
            model: 'product.public.category',
            method: 'search_read',
            kwargs: {
                domain: wUtils.websiteDomain(this),
                fields: ['id', 'name'],
            }
        });
    },
    /**
     *
     * @override
     * @private
     */
    _renderCustomXML: async function (uiFragment) {
        await this._super.apply(this, arguments);
        await this._renderProductCategorySelector(uiFragment);
    },
    /**
     * Renders the product categories option selector content into the provided uiFragment.
     * @private
     * @param {HTMLElement} uiFragment
     */
    _renderProductCategorySelector: async function (uiFragment) {
        const productCategories = await this._fetchProductCategories();
        for (let index in productCategories) {
            this.productCategories[productCategories[index].id] = productCategories[index];
        }
        const productCategoriesSelectorEl = uiFragment.querySelector('[data-name="product_category_opt"]');
        return this._renderSelectUserValueWidgetButtons(productCategoriesSelectorEl, this.productCategories);
    },
    /**
<<<<<<< HEAD
=======
     * Sets default options values.
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
     * @override
     * @private
     */
    _setOptionsDefaultValues: function () {
<<<<<<< HEAD
        this._setOptionValue('productCategoryId', 'all');
        this._super.apply(this, arguments);
    },
=======
        this._super.apply(this, arguments);
        const templateKeys = this.$el.find("we-select[data-attribute-name='templateKey'] we-selection-items we-button");
        if (templateKeys.length > 0) {
            this._setOptionValue('templateKey', templateKeys.attr('data-select-data-attribute'));
        }
        const productCategories = this.$el.find("we-select[data-attribute-name='productCategoryId'] we-selection-items we-button");
        if (productCategories.length > 0) {
            this._setOptionValue('productCategoryId', productCategories.attr('data-select-data-attribute'));
        }
    },

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
});

options.registry.dynamic_snippet_products = dynamicSnippetProductsOptions;

return dynamicSnippetProductsOptions;
});
