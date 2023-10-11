odoo.define('website.editor.link', function (require) {
'use strict';

var weWidgets = require('wysiwyg.widgets');
var wUtils = require('website.utils');

weWidgets.LinkTools.include({
    custom_events: _.extend({}, weWidgets.LinkTools.prototype.custom_events || {}, {
        website_url_chosen: '_onAutocompleteClose',
    }),
    LINK_DEBOUNCE: 1000,

    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
        this._adaptPageAnchor = _.debounce(this._adaptPageAnchor, this.LINK_DEBOUNCE);
    },
    /**
     * Allows the URL input to propose existing website pages.
     *
     * @override
     */
    start: async function () {
        var def = await this._super.apply(this, arguments);
        const options = {
            position: {
                collision: 'flip flipfit',
            },
            classes: {
                "ui-autocomplete": 'o_website_ui_autocomplete'
            },
            body: this.$editable[0].ownerDocument.body,
        };
        wUtils.autocompleteWithPages(this, this.$('input[name="url"]'), options);
        this._adaptPageAnchor();
        return def;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _adaptPageAnchor: function () {
<<<<<<< HEAD
        const urlInputValue = this.$('input[name="url"]').val();
        const $pageAnchor = this.$('.o_link_dialog_page_anchor');
        const isFromWebsite = urlInputValue[0] === '/';
        const $selectMenu = this.$('we-selection-items[name="link_anchor"]');

        if ($selectMenu.data("anchor-for") !== urlInputValue) { // avoid useless query
            $pageAnchor.toggleClass('d-none', !isFromWebsite);
            $selectMenu.empty();
            const always = () => {
                const anchor = `#${urlInputValue.split('#')[1]}`;
                let weTogglerText = '\u00A0';
                if (anchor) {
                    const weButtonEls = $selectMenu[0].querySelectorAll('we-button');
                    if (Array.from(weButtonEls).some(el => el.textContent === anchor)) {
                        weTogglerText = anchor;
                    }
                }
                $pageAnchor[0].querySelector('we-toggler').textContent = weTogglerText;
            };
            const urlWithoutHash = urlInputValue.split("#")[0];
            wUtils.loadAnchors(urlWithoutHash, this.$editable[0].ownerDocument.body).then(anchors => {
                for (const anchor of anchors) {
                    const $option = $('<we-button class="dropdown-item">');
                    $option.text(anchor);
                    $option.data('value', anchor);
                    $selectMenu.append($option);
                }
                always();
            }).guardedCatch(always);
=======
        var urlInputValue = this.$('input[name="url"]').val();
        var $pageAnchor = this.$('.o_link_dialog_page_anchor');
        if (!$pageAnchor.length) {
            return;
        }
        var isFromWebsite = urlInputValue[0] === '/';
        var $selectMenu = this.$('select[name="link_anchor"]');
        var $anchorsLoading = this.$('.o_anchors_loading');

        if ($selectMenu.data("anchor-for") !== urlInputValue) { // avoid useless query
            $anchorsLoading.removeClass('d-none');
            $pageAnchor.toggleClass('d-none', !isFromWebsite);
            $selectMenu.empty();
            const urlWithoutHash = urlInputValue.split("#")[0];
            wUtils.loadAnchors(urlWithoutHash).then(function (anchors) {
                _.each(anchors, function (anchor) {
                    $selectMenu.append($('<option>', {text: anchor}));
                });
                always();
            }).guardedCatch(always);
        } else {
            always();
        }

        function always() {
            $anchorsLoading.addClass('d-none');
            const anchor = `#${urlInputValue.split('#')[1]}`;
            let anchorIndex = -1;
            if (anchor) {
                const optionEls = $selectMenu[0].querySelectorAll('option');
                anchorIndex = Array.from(optionEls).findIndex(el => el.textContent === anchor);
            }
            $selectMenu.prop("selectedIndex", anchorIndex);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        $selectMenu.data("anchor-for", urlInputValue);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onAutocompleteClose: function () {
        this._onURLInput();
    },
    /**
     * @todo this should not be an event handler anymore in master
     * @private
     * @param {Event} ev
     */
    _onAnchorChange: function (ev) {
        const anchorValue = $(ev.currentTarget).data('value');
        const $urlInput = this.$('[name="url"]');
        let urlInputValue = $urlInput.val();
        if (urlInputValue.indexOf('#') > -1) {
            urlInputValue = urlInputValue.substr(0, urlInputValue.indexOf('#'));
        }
        $urlInput.val(urlInputValue + anchorValue);
    },
    /**
     * @override
     */
    _onURLInput: function () {
        this._super.apply(this, arguments);
        this._adaptPageAnchor();
    },
    /**
     * @override
     * @param {Event} ev
     */
    _onPickSelectOption(ev) {
        if (ev.currentTarget.closest('[name="link_anchor"]')) {
            this._onAnchorChange(ev);
        }
        this._super(...arguments);
    },
});
});
