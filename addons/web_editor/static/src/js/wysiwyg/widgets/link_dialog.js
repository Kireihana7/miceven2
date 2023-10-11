odoo.define('wysiwyg.widgets.LinkDialog', function (require) {
'use strict';

const Dialog = require('wysiwyg.widgets.Dialog');
const Link = require('wysiwyg.widgets.Link');


// This widget is there only to extend Link and be instantiated by LinkDialog.
const _DialogLinkWidget = Link.extend({
    template: 'wysiwyg.widgets.link',
    events: _.extend({}, Link.prototype.events || {}, {
        'change [name="link_style_color"]': '_onTypeChange',
    }),

    /**
<<<<<<< HEAD
=======
     * @constructor
     * @param {Boolean} linkInfo.isButton - whether if the target is a button element.
     */
    init: function (parent, options, editable, linkInfo) {
        this.options = options || {};
        this._super(parent, _.extend({
            title: _t("Link to"),
        }, this.options));

        this.trigger_up('getRecordInfo', {
            recordInfo: this.options,
            callback: recordInfo => {
                _.defaults(this.options, recordInfo);
            },
        });

        this.data = linkInfo || {};
        this.isButton = this.data.isButton;
        const isButtonLink = this.isButton || (this.data.range && this.data.range.isOnAnchor() && this.data.className.includes("btn-link"));
        // Using explicit type 'link' to preserve style when the target is <button class="...btn-link"/>.
        this.colorsData = [
            {type: isButtonLink ? 'link' : '', label: _t("Link"), btnPreview: 'link'},
            {type: 'primary', label: _t("Primary"), btnPreview: 'primary'},
            {type: 'secondary', label: _t("Secondary"), btnPreview: 'secondary'},
            // Note: by compatibility the dialog should be able to remove old
            // colors that were suggested like the BS status colors or the
            // alpha -> epsilon classes. This is currently done by removing
            // all btn-* classes anyway.
        ];

        this.editable = editable;
        this.data.className = "";
        this.data.iniClassName = "";

        var r = this.data.range;
        this.needLabel = !r || (r.sc === r.ec && r.so === r.eo);

        if (this.data.range) {
            const $el = $(this.data.range.sc).filter(this.isButton ? "button" : "a");
            this.data.iniClassName = $el.attr("class") || "";
            this.colorCombinationClass = false;
            let $node = $el;
            while ($node.length && !$node.is('body')) {
                const className = $node.attr('class') || '';
                const m = className.match(/\b(o_cc\d+)\b/g);
                if (m) {
                    this.colorCombinationClass = m[0];
                    break;
                }
                $node = $node.parent();
            }
            this.data.className = this.data.iniClassName.replace(/(^|\s+)btn(-[a-z0-9_-]*)?/gi, ' ');

            var is_link = this.data.range.isOnAnchor();

            var sc = r.sc;
            var so = r.so;
            var ec = r.ec;
            var eo = r.eo;

            var nodes;
            if (!is_link) {
                if (sc.tagName) {
                    sc = dom.firstChild(so ? sc.childNodes[so] : sc);
                    so = 0;
                } else if (so !== sc.textContent.length) {
                    if (sc === ec) {
                        ec = sc = sc.splitText(so);
                        eo -= so;
                    } else {
                        sc = sc.splitText(so);
                    }
                    so = 0;
                }
                if (ec.tagName) {
                    ec = dom.lastChild(eo ? ec.childNodes[eo-1] : ec);
                    eo = ec.textContent.length;
                } else if (eo !== ec.textContent.length) {
                    ec.splitText(eo);
                }

                nodes = dom.listBetween(sc, ec);

                // browsers can't target a picture or void node
                if (dom.isVoid(sc) || dom.isImg(sc)) {
                    so = dom.listPrev(sc).length-1;
                    sc = sc.parentNode;
                }
                if (dom.isBR(ec)) {
                    eo = dom.listPrev(ec).length-1;
                    ec = ec.parentNode;
                } else if (dom.isVoid(ec) || dom.isImg(sc)) {
                    eo = dom.listPrev(ec).length;
                    ec = ec.parentNode;
                }

                this.data.range = range.create(sc, so, ec, eo);
                $(editable).data("range", this.data.range);
                this.data.range.select();
            } else {
                nodes = dom.ancestor(sc, dom.isAnchor).childNodes;
            }

            if (dom.isImg(sc) && nodes.indexOf(sc) === -1) {
                nodes.push(sc);
            }
            if (nodes.length > 1 || dom.ancestor(nodes[0], dom.isImg)) {
                var text = "";
                this.data.images = [];
                for (var i=0; i<nodes.length; i++) {
                    if (dom.ancestor(nodes[i], dom.isImg)) {
                        this.data.images.push(dom.ancestor(nodes[i], dom.isImg));
                        text += '[IMG]';
                    } else if (!is_link && nodes[i].nodeType === 1) {
                        // just use text nodes from listBetween
                    } else if (!is_link && i===0) {
                        text += nodes[i].textContent.slice(so, Infinity);
                    } else if (!is_link && i===nodes.length-1) {
                        text += nodes[i].textContent.slice(0, eo);
                    } else {
                        text += nodes[i].textContent;
                    }
                }
                this.data.text = text;
            }
        }

        this.data.text = this.data.text.replace(/[ \t\r\n]+/g, ' ');

        var allBtnClassSuffixes = /(^|\s+)btn(-[a-z0-9_-]*)?/gi;
        var allBtnShapes = /\s*(rounded-circle|flat)\s*/gi;
        this.data.className = this.data.iniClassName
            .replace(allBtnClassSuffixes, ' ')
            .replace(allBtnShapes, ' ');
        // 'o_submit' class will force anchor to be handled as a button in linkdialog.
        if (/(?:s_website_form_send|o_submit)/.test(this.data.className)) {
            this.isButton = true;
        }
    },
    /**
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
     * @override
     */
    start: function () {
        this.buttonOptsCollapseEl = this.el.querySelector('#o_link_dialog_button_opts_collapse');
        this.$styleInputs = this.$('input.link-style');
        this.$styleInputs.prop('checked', false).filter('[value=""]').prop('checked', true);
<<<<<<< HEAD
        if (this.data.isNewWindow) {
            this.$('we-button.o_we_checkbox_wrapper').toggleClass('active', true);
=======
        if (this.data.iniClassName) {
            _.each(this.$('input[name="link_style_color"], select[name="link_style_size"] > option, select[name="link_style_shape"] > option'), el => {
                const $option = $(el);
                const value = $option.val();
                if (!value) {
                    return;
                }
                const subValues = value.split(',');
                let active = true;
                for (let i = 0; i < subValues.length; i++) {
                    const classPrefix = new RegExp('(^|btn-| |btn-outline-|btn-fill-)' + subValues[i]);
                    active = active && classPrefix.test(this.data.iniClassName);
                }
                if (active) {
                    if ($option.is("input")) {
                        $option.prop("checked", true);
                    } else {
                        $option.parent().find('option').removeAttr('selected').removeProp('selected');
                        $option.parent().val($option.val());
                        $option.attr('selected', 'selected').prop('selected', 'selected');
                    }
                }
            });
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    save: function () {
        var data = this._getData();
        if (data === null) {
            var $url = this.$('input[name="url"]');
            $url.closest('.o_url_input').addClass('o_has_error').find('.form-control, .form-select').addClass('is-invalid');
            $url.focus();
            return Promise.reject();
        }
        this.data.content = data.content;
        this.data.url = data.url;
        var allWhitespace = /\s+/gi;
        var allStartAndEndSpace = /^\s+|\s+$/gi;
        var allBtnTypes = /(^|[ ])(btn-secondary|btn-success|btn-primary|btn-info|btn-warning|btn-danger)([ ]|$)/gi;
        this.data.classes = data.classes.replace(allWhitespace, ' ').replace(allStartAndEndSpace, '');
        if (data.classes.replace(allBtnTypes, ' ')) {
            this.data.style = {
                'background-color': '',
                'color': '',
            };
        }
        this.data.isNewWindow = data.isNewWindow;
        this.final_data = this.data;
        return Promise.resolve();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _adaptPreview: function () {
        var data = this._getData();
        if (data === null) {
            return;
        }
        const attrs = {
            target: '_blank',
            href: data.url && data.url.length ? data.url : '#',
            class: `${data.classes.replace(/float-\w+/, '')} o_btn_preview`,
        };

        const $linkPreview = this.$("#link-preview");
        $linkPreview.attr(attrs);
        this._updateLinkContent($linkPreview, data, { force: true });
    },
    /**
     * @override
     */
<<<<<<< HEAD
    _doStripDomain: function () {
        return this.$('#o_link_dialog_url_strip_domain').prop('checked');
    },
    /**
     * @override
     */
    _getIsNewWindowFormRow() {
        return this.$('input[name="is_new_window"]').closest('.row');
    },
    /**
     * @override
     */
    _getLinkOptions: function () {
        const options = [
            'input[name="link_style_color"]',
            'select[name="link_style_size"] > option',
            'select[name="link_style_shape"] > option',
        ];
        return this.$(options.join(','));
    },
    /**
     * @override
     */
    _getLinkShape: function () {
        return this.$('select[name="link_style_shape"]').val() || '';
    },
    /**
     * @override
     */
    _getLinkSize: function () {
        return this.$('select[name="link_style_size"]').val() || '';
    },
    /**
     * @override
     */
    _getLinkType: function () {
        return this.$('input[name="link_style_color"]:checked').val() || '';
=======
    _getData: function () {
        var $url = this.$('input[name="url"]');
        var url = $url.val();
        var label = _.escape(this.$('input[name="label"]').val() || url);

        if (label && this.data.images) {
            for (var i = 0; i < this.data.images.length; i++) {
                label = label.replace(/\[IMG\]/, this.data.images[i].outerHTML);
            }
        }

        if (!this.isButton && $url.prop('required') && (!url || !$url[0].checkValidity())) {
            return null;
        }

        const type = this.$('input[name="link_style_color"]:checked').val() || '';
        const size = this.$('select[name="link_style_size"]').val() || '';
        const shape = this.$('select[name="link_style_shape"]').val() || '';
        const shapes = shape ? shape.split(',') : [];
        const style = ['outline', 'fill'].includes(shapes[0]) ? `${shapes[0]}-` : '';
        const shapeClasses = shapes.slice(style ? 1 : 0).join(' ');
        const classes = (this.data.className || '') +
            (type ? (` btn btn-${style}${type}`) : '') +
            (shapeClasses ? (` ${shapeClasses}`) : '') +
            (size ? (' btn-' + size) : '');
        var isNewWindow = this.$('input[name="is_new_window"]').prop('checked');
        if (url.indexOf('@') >= 0 && url.indexOf('mailto:') < 0 && !url.match(/^http[s]?/i)) {
            url = ('mailto:' + url);
        } else if (url.indexOf(location.origin) === 0 && this.$('#o_link_dialog_url_strip_domain').prop("checked")) {
            url = url.slice(location.origin.length);
        }
        var allWhitespace = /\s+/gi;
        var allStartAndEndSpace = /^\s+|\s+$/gi;
        return {
            label: label,
            url: url,
            classes: classes.replace(allWhitespace, ' ').replace(allStartAndEndSpace, ''),
            isNewWindow: isNewWindow,
        };
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    /**
     * @private
     */
    _isFromAnotherHostName: function (url) {
        if (url.includes(window.location.hostname)) {
            return false;
        }
        try {
            const Url = URL || window.URL || window.webkitURL;
            const urlObj = url.startsWith('/') ? new Url(url, window.location.origin) : new Url(url);
            return (urlObj.origin !== window.location.origin);
        } catch (_ignored) {
            return true;
        }
    },
    /**
     * @override
     */
    _isNewWindow: function (url) {
        if (this.options.forceNewWindow) {
            return this._isFromAnotherHostName(url);
        } else {
            return this.$('input[name="is_new_window"]').prop('checked');
        }
    },
    /**
     * @override
     */
    _setSelectOption: function ($option, active) {
        if ($option.is("input")) {
            $option.prop("checked", active);
        } else if (active) {
            $option.parent().find('option').removeAttr('selected').removeProp('selected');
            $option.parent().val($option.val());
            $option.attr('selected', 'selected').prop('selected', 'selected');
        }
    },
    /**
     * @override
     */
    _updateOptionsUI: function () {
        const el = this.el.querySelector('[name="link_style_color"]:checked');
        $(this.buttonOptsCollapseEl).collapse(el && el.value ? 'show' : 'hide');
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onTypeChange() {
        this._updateOptionsUI();
    },
    /**
     * @override
     */
    _onURLInput: function () {
        this._super(...arguments);
        this.$('#o_link_dialog_url_input').closest('.o_url_input').removeClass('o_has_error').find('.form-control, .form-select').removeClass('is-invalid');
        this._adaptPreview();
    },
});

/**
 * Allows to customize link content and style.
 */
const LinkDialog = Dialog.extend({
    init: function (parent, ...args) {
        this._super(...arguments);
        this.linkWidget = this.getLinkWidget(...args);
    },
    start: async function () {
        const res = await this._super(...arguments);
        await this.linkWidget.appendTo(this.$el);
        return res;
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Returns an instance of the widget that will be attached to the body of the
     * link dialog. One may overwrite this function and return an instance of
     * another widget to change the default logic.
     * @param {...any} args
     */
    getLinkWidget: function (...args) {
        return new _DialogLinkWidget(this, ...args);
    },

    /**
     * @override
     */
    save: function () {
        const _super = this._super.bind(this);
        const saveArguments = arguments;
        return this.linkWidget.save().then(() => {
            this.final_data = this.linkWidget.final_data;
            return _super(...saveArguments);
        });
    },
});

return LinkDialog;
});
