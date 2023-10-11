odoo.define('point_of_sale.ProductsWidgetControlPanel', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { debounce } = require("@web/core/utils/timing");

    const { onMounted, onWillUnmount, useRef } = owl;

    class ProductsWidgetControlPanel extends PosComponent {
<<<<<<< HEAD
        setup() {
            super.setup();
            this.searchWordInput = useRef('search-word-input-product');
=======
        constructor() {
            super(...arguments);
            this.searchWordInput = useRef('search-word-input');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            this.updateSearch = debounce(this.updateSearch, 100);

            onMounted(() => {
                this.env.posbus.on('search-product-from-info-popup', this, this.searchProductFromInfo)
            });

            onWillUnmount(() => {
                this.env.posbus.off('search-product-from-info-popup', this);
            });
        }
        _clearSearch() {
            this.searchWordInput.el.value = '';
            this.trigger('clear-search');
        }
        get displayCategImages() {
            return Object.values(this.env.pos.db.category_by_id).some(categ => categ.has_image) && !this.env.isMobile;
        }
        updateSearch(event) {
            this.trigger('update-search', event.target.value);
            if (event.key === 'Enter') {
                // We are passing the searchWordInput ref so that when necessary,
                // it can be modified by the parent.
                this.trigger('try-add-product', { searchWordInput: this.searchWordInput });
            }
        }
        async _onPressEnterKey() {
            if (!this.searchWordInput.el.value) return;
            this.trigger('load-products-from-server');
        }
        searchProductFromInfo(productName) {
            this.searchWordInput.el.value = productName;
            this.trigger('switch-category', 0);
            this.trigger('update-search', productName);
        }
        _toggleMobileSearchbar() {
            this.trigger('toggle-mobile-searchbar');
        }
    }
    ProductsWidgetControlPanel.template = 'ProductsWidgetControlPanel';

    Registries.Component.add(ProductsWidgetControlPanel);

    return ProductsWidgetControlPanel;
});
