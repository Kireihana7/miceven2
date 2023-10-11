odoo.define('website.s_dynamic_snippet_carousel', function (require) {
'use strict';

const publicWidget = require('web.public.widget');
const DynamicSnippet = require('website.s_dynamic_snippet');
const config = require('web.config');

const DynamicSnippetCarousel = DynamicSnippet.extend({
    selector: '.s_dynamic_snippet_carousel',
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.template_key = 'website.s_dynamic_snippet.carousel';
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
<<<<<<< HEAD
=======
     */
    _getQWebRenderOptions: function () {
        return Object.assign(
            this._super.apply(this, arguments),
            {
                interval: parseInt(this.$target[0].dataset.carouselInterval),
            },
        );
    },
    /**
     * @deprecated
     * @todo remove me in master, this was wrongly named and was supposed to
     * override _getQWebRenderOptions. This is kept for potential custo in
     * stable, although note that without hacks, calling this._super here just
     * crashes.
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
     */
    _getQWebRenderOptions: function () {
        return Object.assign(
            this._super.apply(this, arguments),
            {
                interval: parseInt(this.$target[0].dataset.carouselInterval),
<<<<<<< HEAD
                rowPerSlide: parseInt(config.device.isMobile ? 1 : this.$target[0].dataset.rowPerSlide || 1),
                arrowPosition: this.$target[0].dataset.arrowPosition || '',
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            },
        );
    },
});
publicWidget.registry.dynamic_snippet_carousel = DynamicSnippetCarousel;

return DynamicSnippetCarousel;
});
