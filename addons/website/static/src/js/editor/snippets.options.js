odoo.define('website.editor.snippets.options', function (require) {
'use strict';

const {ColorpickerWidget} = require('web.Colorpicker');
var core = require('web.core');
const { loadBundle, loadCSS } = require("@web/core/assets");
var Dialog = require('web.Dialog');
<<<<<<< HEAD
const {Markup, sprintf} = require('web.utils');
=======
const dom = require('web.dom');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
const weUtils = require('web_editor.utils');
var options = require('web_editor.snippets.options');
const wLinkPopoverWidget = require('@website/js/widgets/link_popover_widget')[Symbol.for("default")];
const wUtils = require('website.utils');
const {isImageSupportedForStyle} = require('web_editor.image_processing');
require('website.s_popup_options');
const {Domain} = require('@web/core/domain');

var _t = core._t;
var qweb = core.qweb;

const InputUserValueWidget = options.userValueWidgetsRegistry['we-input'];
const SelectUserValueWidget = options.userValueWidgetsRegistry['we-select'];
const Many2oneUserValueWidget = options.userValueWidgetsRegistry['we-many2one'];

options.UserValueWidget.include({
    loadMethodsData() {
        this._super(...arguments);

        // Method names are sorted alphabetically by default. Exception here:
        // we make sure, customizeWebsiteVariable is considered after
        // customizeWebsiteViews so that the variable is used to show to active
        // value when both methods are used at the same time.
        // TODO find a better way.
        const indexVariable = this._methodsNames.indexOf('customizeWebsiteVariable');
        if (indexVariable >= 0) {
            const indexView = this._methodsNames.indexOf('customizeWebsiteViews');
            if (indexView >= 0) {
                this._methodsNames[indexVariable] = 'customizeWebsiteViews';
                this._methodsNames[indexView] = 'customizeWebsiteVariable';
            }
        }
    },
});

Many2oneUserValueWidget.include({
    /**
     * @override
     */
    async _getSearchDomain() {
        // Add the current website's domain if the model has a website_id field.
        // Note that the `_rpc` method is cached in Many2X user value widget,
        // see `_rpcCache`.
        const websiteIdField = await this._rpc({
            model: this.options.model,
            method: "fields_get",
            args: [["website_id"]],
        });
        const modelHasWebsiteId = !!websiteIdField["website_id"];
        if (modelHasWebsiteId && !this.options.domain.find(arr => arr[0] === "website_id")) {
            this.options.domain =
                Domain.and([this.options.domain, wUtils.websiteDomain(this)]).toList();
        }
        return this.options.domain;
    },
});

const UrlPickerUserValueWidget = InputUserValueWidget.extend({
    custom_events: _.extend({}, InputUserValueWidget.prototype.custom_events || {}, {
        'website_url_chosen': '_onWebsiteURLChosen',
    }),
    events: _.extend({}, InputUserValueWidget.prototype.events || {}, {
        'click .o_we_redirect_to': '_onRedirectTo',
    }),

    /**
     * @override
     */
    start: async function () {
        await this._super(...arguments);
        const linkButton = document.createElement('we-button');
        const icon = document.createElement('i');
        icon.classList.add('fa', 'fa-fw', 'fa-external-link')
        linkButton.classList.add('o_we_redirect_to');
        linkButton.title = _t("Redirect to URL in a new tab");
        linkButton.appendChild(icon);
        this.containerEl.appendChild(linkButton);
<<<<<<< HEAD
        this.el.classList.add('o_we_large');
        this.inputEl.classList.add('text-start');
=======
        this.el.classList.add('o_we_large_input');
        this.inputEl.classList.add('text-left');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        const options = {
            position: {
                collision: 'flip flipfit',
            },
            classes: {
                "ui-autocomplete": 'o_website_ui_autocomplete'
            },
<<<<<<< HEAD
            body: this.getParent().$target[0].ownerDocument.body,
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        };
        wUtils.autocompleteWithPages(this, $(this.inputEl), options);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called when the autocomplete change the input value.
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onWebsiteURLChosen: function (ev) {
        this._value = this.inputEl.value;
        this._onUserValueChange(ev);
    },
    /**
     * Redirects to the URL the widget currently holds.
     *
     * @private
     */
    _onRedirectTo: function () {
        if (this._value) {
            window.open(this._value, '_blank');
        }
    },
});

const FontFamilyPickerUserValueWidget = SelectUserValueWidget.extend({
    events: _.extend({}, SelectUserValueWidget.prototype.events || {}, {
        'click .o_we_add_google_font_btn': '_onAddGoogleFontClick',
        'click .o_we_delete_google_font_btn': '_onDeleteGoogleFontClick',
    }),
    fontVariables: [], // Filled by editor menu when all options are loaded

    /**
     * @override
     */
    start: async function () {
        const style = window.getComputedStyle(this.$target[0].ownerDocument.documentElement);
        const nbFonts = parseInt(weUtils.getCSSVariableValue('number-of-fonts', style));
        // User fonts served by google server.
        const googleFontsProperty = weUtils.getCSSVariableValue('google-fonts', style);
        this.googleFonts = googleFontsProperty ? googleFontsProperty.split(/\s*,\s*/g) : [];
        this.googleFonts = this.googleFonts.map(font => font.substring(1, font.length - 1)); // Unquote
        // Local user fonts.
        const googleLocalFontsProperty = weUtils.getCSSVariableValue('google-local-fonts', style);
        this.googleLocalFonts = googleLocalFontsProperty ?
            googleLocalFontsProperty.slice(1, -1).split(/\s*,\s*/g) : [];
        // If a same font exists both remotely and locally, we remove the remote
        // font to prioritize the local font. The remote one will never be
        // displayed or loaded as long as the local one exists.
        this.googleFonts = this.googleFonts.filter(font => {
            const localFonts = this.googleLocalFonts.map(localFont => localFont.split(":")[0]);
            return localFonts.indexOf(`'${font}'`) === -1;
        });
        this.allFonts = [];

        await this._super(...arguments);

        const fontsToLoad = [];
        for (const font of this.googleFonts) {
            const fontURL = `https://fonts.googleapis.com/css?family=${encodeURIComponent(font).replace(/%20/g, '+')}`;
            fontsToLoad.push(fontURL);
        }
        for (const font of this.googleLocalFonts) {
            const attachmentId = font.split(/\s*:\s*/)[1];
            const fontURL = `/web/content/${encodeURIComponent(attachmentId)}`;
            fontsToLoad.push(fontURL);
        }
        // TODO ideally, remove the <link> elements created once this widget
        // instance is destroyed (although it should not hurt to keep them for
        // the whole backend lifecycle).
        const proms = fontsToLoad.map(async fontURL => loadCSS(fontURL));
        const fontsLoadingProm = Promise.all(proms);

        const fontEls = [];
        const methodName = this.el.dataset.methodName || 'customizeWebsiteVariable';
        const variable = this.el.dataset.variable;
        const themeFontsNb = nbFonts - (this.googleLocalFonts.length + this.googleFonts.length);
        _.times(nbFonts, fontNb => {
            const realFontNb = fontNb + 1;
            const fontKey = weUtils.getCSSVariableValue(`font-number-${realFontNb}`, style);
            this.allFonts.push(fontKey);
            let fontName = fontKey.slice(1, -1); // Unquote
            let fontFamily = fontName;
            const isSystemFonts = fontName === "SYSTEM_FONTS";
            if (isSystemFonts) {
                fontName = _t("System Fonts");
                fontFamily = 'var(--o-system-fonts)';
            }
            const fontEl = document.createElement('we-button');
            // TODO: Remove me in master;
            fontEl.classList.add(`o_we_option_font_${realFontNb}`);
            fontEl.setAttribute('string', fontName);
            fontEl.dataset.variable = variable;
<<<<<<< HEAD
            fontEl.dataset[methodName] = fontKey;
            fontEl.dataset.font = realFontNb;
            fontEl.dataset.fontFamily = fontFamily;
            if ((realFontNb <= themeFontsNb) && !isSystemFonts) {
=======
            fontEl.dataset[methodName] = weUtils.getCSSVariableValue(`font-number-${realFontNb}`, style);
            const font = weUtils.getCSSVariableValue(`font-number-${realFontNb}`, style);
            this.allFonts.push(font);
            fontEl.dataset[methodName] = font;
            fontEl.dataset.font = realFontNb;
            if (realFontNb <= themeFontsNb) {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                // Add the "cloud" icon next to the theme's default fonts
                // because they are served by Google.
                fontEl.appendChild(Object.assign(document.createElement('i'), {
                    role: 'button',
<<<<<<< HEAD
                    className: 'text-info me-2 fa fa-cloud',
=======
                    className: 'text-info ml-2 fa fa-cloud',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                    title: _t("This font is hosted and served to your visitors by Google servers"),
                }));
            }
            fontEls.push(fontEl);
            this.menuEl.appendChild(fontEl);
        });

        if (this.googleLocalFonts.length) {
            const googleLocalFontsEls = fontEls.splice(-this.googleLocalFonts.length);
            googleLocalFontsEls.forEach((el, index) => {
                $(el).append(core.qweb.render('website.delete_google_font_btn', {
                    index: index,
                    local: true,
                }));
            });
        }

        if (this.googleFonts.length) {
            const googleFontsEls = fontEls.splice(-this.googleFonts.length);
            googleFontsEls.forEach((el, index) => {
                $(el).append(core.qweb.render('website.delete_google_font_btn', {
                    index: index,
                }));
            });
        }

        $(this.menuEl).append($(core.qweb.render('website.add_google_font_btn', {
            variable: variable,
        })));

        return fontsLoadingProm;
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async setValue() {
        await this._super(...arguments);

        // TODO: Remove me in master
        for (const className of this.menuTogglerEl.classList) {
            if (className.match(/^o_we_option_font_\d+$/)) {
                this.menuTogglerEl.classList.remove(className);
            }
        }
        const activeWidget = this._userValueWidgets.find(widget => !widget.isPreviewed() && widget.isActive());
        if (activeWidget) {
<<<<<<< HEAD
            this.menuTogglerEl.style.fontFamily = activeWidget.el.dataset.fontFamily;
            // TODO: Remove me in master
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            this.menuTogglerEl.classList.add(`o_we_option_font_${activeWidget.el.dataset.font}`);
        }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onAddGoogleFontClick: function (ev) {
        const variable = $(ev.currentTarget).data('variable');
        const dialog = new Dialog(this, {
            title: _t("Add a Google Font"),
            $content: $(core.qweb.render('website.dialog.addGoogleFont')),
            buttons: [
                {
                    text: _t("Save & Reload"),
                    classes: 'btn-primary',
                    click: async () => {
                        const inputEl = dialog.el.querySelector('.o_input_google_font');
                        // if font page link (what is expected)
                        let m = inputEl.value.match(/\bspecimen\/([\w+]+)/);
                        if (!m) {
                            // if embed code (so that it works anyway if the user put the embed code instead of the page link)
                            m = inputEl.value.match(/\bfamily=([\w+]+)/);
                            if (!m) {
                                inputEl.classList.add('is-invalid');
                                return;
                            }
                        }

                        let isValidFamily = false;

                        try {
                            // Font family is an encoded query parameter:
                            // "Open+Sans" needs to remain "Open+Sans".
                            const result = await fetch("https://fonts.googleapis.com/css?family=" + m[1] + ':300,300i,400,400i,700,700i', {method: 'HEAD'});
                            // Google fonts server returns a 400 status code if family is not valid.
                            if (result.ok) {
                                isValidFamily = true;
                            }
                        } catch (error) {
                            console.error(error);
                        }

                        if (!isValidFamily) {
                            inputEl.classList.add('is-invalid');
                            return;
                        }

                        const font = m[1].replace(/\+/g, ' ');
                        const googleFontServe = dialog.el.querySelector('#google_font_serve').checked;
                        const fontName = `'${font}'`;
                        // If the font already exists, it will only be added if
                        // the user chooses to add it locally when it is already
                        // imported from the Google Fonts server.
                        const fontExistsLocally = this.googleLocalFonts.some(localFont => localFont.split(':')[0] === fontName);
                        const fontExistsOnServer = this.allFonts.includes(fontName);
                        const preventFontAddition = fontExistsLocally || (fontExistsOnServer && googleFontServe);
                        if (preventFontAddition) {
                            inputEl.classList.add('is-invalid');
                            // Show custom validity error message.
                            inputEl.setCustomValidity(_t("This font already exists, you can only add it as a local font to replace the server version."));
                            inputEl.reportValidity();
                            return;
                        }
                        if (googleFontServe) {
                            this.googleFonts.push(font);
                        } else {
                            this.googleLocalFonts.push(`'${font}': ''`);
                        }
                        this.trigger_up('google_fonts_custo_request', {
                            values: {[variable]: `'${font}'`},
                            googleFonts: this.googleFonts,
                            googleLocalFonts: this.googleLocalFonts,
                        });
                    },
                },
                {
                    text: _t("Discard"),
                    close: true,
                },
            ],
        });
        dialog.open();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onDeleteGoogleFontClick: async function (ev) {
        ev.preventDefault();
        const values = {};

        const save = await new Promise(resolve => {
            Dialog.confirm(this, _t("Deleting a font requires a reload of the page. This will save all your changes and reload the page, are you sure you want to proceed?"), {
                confirm_callback: () => resolve(true),
                cancel_callback: () => resolve(false),
            });
        });
        if (!save) {
            return;
        }

        // Remove Google font
        const googleFontIndex = parseInt(ev.target.dataset.fontIndex);
        const isLocalFont = ev.target.dataset.localFont;
        let googleFontName;
        if (isLocalFont) {
            const googleFont = this.googleLocalFonts[googleFontIndex].split(':');
            // Remove double quotes
            googleFontName = googleFont[0].substring(1, googleFont[0].length - 1);
            values['delete-font-attachment-id'] = googleFont[1];
            this.googleLocalFonts.splice(googleFontIndex, 1);
        } else {
            googleFontName = this.googleFonts[googleFontIndex];
            this.googleFonts.splice(googleFontIndex, 1);
        }

        // Adapt font variable indexes to the removal
<<<<<<< HEAD
        const style = window.getComputedStyle(this.$target[0].ownerDocument.documentElement);
=======
        const style = window.getComputedStyle(document.documentElement);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        _.each(FontFamilyPickerUserValueWidget.prototype.fontVariables, variable => {
            const value = weUtils.getCSSVariableValue(variable, style);
            if (value.substring(1, value.length - 1) === googleFontName) {
                // If an element is using the google font being removed, reset
                // it to the theme default.
                values[variable] = 'null';
            }
        });

        this.trigger_up('google_fonts_custo_request', {
            values: values,
            googleFonts: this.googleFonts,
            googleLocalFonts: this.googleLocalFonts,
        });
    },
});

const GPSPicker = InputUserValueWidget.extend({
    events: { // Explicitly not consider all InputUserValueWidget events
        'blur input': '_onInputBlur',
    },

    /**
     * @constructor
     */
    init() {
        this._super(...arguments);
        this._gmapCacheGPSToPlace = {};

        // The google API will be loaded inside the website iframe. Let's try
        // not having to load it in the backend too and just using the iframe
        // google object instead.
        this.contentWindow = this.$target[0].ownerDocument.defaultView;
    },
    /**
     * @override
     */
    async willStart() {
        await this._super(...arguments);
        this._gmapLoaded = await new Promise(resolve => {
            this.trigger_up('gmap_api_request', {
                editableMode: true,
                configureIfNecessary: true,
                onSuccess: key => {
                    if (!key) {
                        resolve(false);
                        return;
                    }

                    // TODO see _notifyGMapError, this tries to trigger an error
                    // early but this is not consistent with new gmap keys.
                    this._nearbySearch('(50.854975,4.3753899)', !!key)
                        .then(place => resolve(!!place));
                },
            });
        });
        if (!this._gmapLoaded && !this._gmapErrorNotified) {
            this.trigger_up('user_value_widget_critical');
            return;
        }
    },
    /**
     * @override
     */
    async start() {
        await this._super(...arguments);
        this.el.classList.add('o_we_large');
        if (!this._gmapLoaded) {
            return;
        }

        this._gmapAutocomplete = new this.contentWindow.google.maps.places.Autocomplete(this.inputEl, {types: ['geocode']});
        this.contentWindow.google.maps.event.addListener(this._gmapAutocomplete, 'place_changed', this._onPlaceChanged.bind(this));
    },
    /**
     * @override
     */
    destroy() {
        this._super(...arguments);

        // Without this, the google library injects elements inside the backend
        // DOM but do not remove them once the editor is left. Notice that
        // this is also done when the widget is destroyed for another reason
        // than leaving the editor, but if the google API needs that container
        // again afterwards, it will simply recreate it.
        for (const el of document.body.querySelectorAll('.pac-container')) {
            el.remove();
        }
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    getMethodsParams: function (methodName) {
        return Object.assign({gmapPlace: this._gmapPlace || {}}, this._super(...arguments));
    },
    /**
     * @override
     */
    async setValue() {
        await this._super(...arguments);
        if (!this._gmapLoaded) {
            return;
        }

        this._gmapPlace = await this._nearbySearch(this._value);

        if (this._gmapPlace) {
            this.inputEl.value = this._gmapPlace.formatted_address;
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {string} gps
     * @param {boolean} [notify=true]
     * @returns {Promise}
     */
    async _nearbySearch(gps, notify = true) {
        if (this._gmapCacheGPSToPlace[gps]) {
            return this._gmapCacheGPSToPlace[gps];
        }

        const p = gps.substring(1).slice(0, -1).split(',');
<<<<<<< HEAD
        const location = new this.contentWindow.google.maps.LatLng(p[0] || 0, p[1] || 0);
        return new Promise(resolve => {
            const service = new this.contentWindow.google.maps.places.PlacesService(document.createElement('div'));
=======
        const location = new google.maps.LatLng(p[0] || 0, p[1] || 0);
        return new Promise(resolve => {
            const service = new google.maps.places.PlacesService(document.createElement('div'));
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            service.nearbySearch({
                // Do a 'nearbySearch' followed by 'getDetails' to avoid using
                // GMap Geocoder which the user may not have enabled... but
                // ideally Geocoder should be used to get the exact location at
                // those coordinates and to limit billing query count.
                location: location,
                radius: 1,
            }, (results, status) => {
                const GMAP_CRITICAL_ERRORS = [
                    this.contentWindow.google.maps.places.PlacesServiceStatus.REQUEST_DENIED,
                    this.contentWindow.google.maps.places.PlacesServiceStatus.UNKNOWN_ERROR
                ];
                if (status === this.contentWindow.google.maps.places.PlacesServiceStatus.OK) {
                    service.getDetails({
                        placeId: results[0].place_id,
                        fields: ['geometry', 'formatted_address'],
                    }, (place, status) => {
<<<<<<< HEAD
                        if (status === this.contentWindow.google.maps.places.PlacesServiceStatus.OK) {
=======
                        if (status === google.maps.places.PlacesServiceStatus.OK) {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                            this._gmapCacheGPSToPlace[gps] = place;
                            resolve(place);
                        } else if (GMAP_CRITICAL_ERRORS.includes(status)) {
                            if (notify) {
                                this._notifyGMapError();
                            }
                            resolve();
                        }
                    });
                } else if (GMAP_CRITICAL_ERRORS.includes(status)) {
                    if (notify) {
                        this._notifyGMapError();
                    }
                    resolve();
                } else {
                    resolve();
                }
            });
        });
    },
    /**
     * Indicates to the user there is an error with the google map API and
     * re-opens the configuration dialog. For good measures, this also notifies
     * a critical error which normally removes the related snippet entirely.
     *
     * @private
     */
    _notifyGMapError() {
        // TODO this should be better to detect all errors. This is random.
        // When misconfigured (wrong APIs enabled), sometimes Google throw
        // errors immediately (which then reaches this code), sometimes it
        // throws them later (which then induces an error log in the console
        // and random behaviors).
        if (this._gmapErrorNotified) {
            return;
        }
        this._gmapErrorNotified = true;

        this.displayNotification({
            type: 'danger',
            sticky: true,
            message: _t("A Google Map error occurred. Make sure to read the key configuration popup carefully."),
        });
        this.trigger_up('gmap_api_request', {
            editableMode: true,
            reconfigure: true,
            onSuccess: () => {
                this._gmapErrorNotified = false;
            },
        });

        setTimeout(() => this.trigger_up('user_value_widget_critical'));
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onPlaceChanged(ev) {
        const gmapPlace = this._gmapAutocomplete.getPlace();
        if (gmapPlace && gmapPlace.geometry) {
            this._gmapPlace = gmapPlace;
            const location = this._gmapPlace.geometry.location;
            const oldValue = this._value;
            this._value = `(${location.lat()},${location.lng()})`;
            this._gmapCacheGPSToPlace[this._value] = gmapPlace;
            if (oldValue !== this._value) {
                this._onUserValueChange(ev);
            }
        }
    },
    /**
     * @override
     */
    _onInputBlur() {
        // As a stable fix: do not call the _super as we actually don't want
        // input focusout messing with the google map API. Because of this,
        // clicking on google map autocomplete suggestion on Firefox was not
        // working properly. This is kept as an empty function because of stable
        // policy (ensures custo can still extend this).
        // TODO review in master.
    },
});
options.userValueWidgetsRegistry['we-urlpicker'] = UrlPickerUserValueWidget;
options.userValueWidgetsRegistry['we-fontfamilypicker'] = FontFamilyPickerUserValueWidget;
options.userValueWidgetsRegistry['we-gpspicker'] = GPSPicker;

//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

options.Class.include({
    custom_events: _.extend({}, options.Class.prototype.custom_events || {}, {
        'google_fonts_custo_request': '_onGoogleFontsCustoRequest',
    }),
    specialCheckAndReloadMethodsNames: ['customizeWebsiteViews', 'customizeWebsiteVariable', 'customizeWebsiteColor'],

    /**
     * @override
     */
    init() {
        this._super(...arguments);
        // Since the website is displayed in an iframe, its jQuery
        // instance is not the same as the editor. This property allows
        // for easy access to bootstrap plugins (Carousel, Modal, ...).
        // This is only needed because jQuery doesn't send custom events
        // the same way native javascript does. So if a jQuery instance
        // triggers a custom event, only that same jQuery instance will
        // trigger handlers set with `.on`.
        this.$bsTarget = this.ownerDocument.defaultView.$(this.$target[0]);
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @see this.selectClass for parameters
     */
    customizeWebsiteViews: async function (previewMode, widgetValue, params) {
        await this._customizeWebsite(previewMode, widgetValue, params, 'views');
    },
    /**
     * @see this.selectClass for parameters
     */
    customizeWebsiteVariable: async function (previewMode, widgetValue, params) {
        await this._customizeWebsite(previewMode, widgetValue, params, 'variable');
    },
    /**
     * @see this.selectClass for parameters
     */
    customizeWebsiteColor: async function (previewMode, widgetValue, params) {
        await this._customizeWebsite(previewMode, widgetValue, params, 'color');
    },
    /**
     * @see this.selectClass for parameters
     */
    async customizeWebsiteAssets(previewMode, widgetValue, params) {
        await this._customizeWebsite(previewMode, widgetValue, params, 'assets');
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _checkIfWidgetsUpdateNeedReload(widgets) {
        const needReload = await this._super(...arguments);
        if (needReload) {
            return needReload;
        }
        for (const widget of widgets) {
            const methodsNames = widget.getMethodsNames();
            const specialMethodsNames = [];
            // If it's a pageOption, it's most likely to need to reload, so check the widgets.
            if (this.data.pageOptions) {
                specialMethodsNames.push(methodsNames);
            } else {
                for (const methodName of methodsNames) {
                    if (this.specialCheckAndReloadMethodsNames.includes(methodName)) {
                        specialMethodsNames.push(methodName);
                    }
                }
            }
            if (!specialMethodsNames.length) {
                continue;
            }
            let paramsReload = false;
            for (const methodName of specialMethodsNames) {
                if (widget.getMethodsParams(methodName).reload) {
                    paramsReload = true;
                    break;
                }
            }
            if (paramsReload) {
                return true;
            }
        }
        return false;
    },
    /**
     * @override
     */
    _computeWidgetState: async function (methodName, params) {
        switch (methodName) {
            case 'customizeWebsiteViews': {
                return this._getEnabledCustomizeValues(params.possibleValues, true);
            }
            case 'customizeWebsiteVariable': {
                const ownerDocument = this.$target[0].ownerDocument;
                const style = ownerDocument.defaultView.getComputedStyle(ownerDocument.documentElement);
                return weUtils.getCSSVariableValue(params.variable, style);
            }
            case 'customizeWebsiteColor': {
<<<<<<< HEAD
                const ownerDocument = this.$target[0].ownerDocument;
                const style = ownerDocument.defaultView.getComputedStyle(ownerDocument.documentElement);
                return weUtils.getCSSVariableValue(params.color, style);
            }
            case 'customizeWebsiteAssets': {
                return this._getEnabledCustomizeValues(params.possibleValues, false);
=======
                // TODO adapt in master
                const bugfixedValue = weUtils.getCSSVariableValue(`bugfixed-${params.color}`);
                if (bugfixedValue) {
                    return bugfixedValue;
                }
                return weUtils.getCSSVariableValue(params.color);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
        }
        return this._super(...arguments);
    },
    /**
     * @private
     */
    _customizeWebsite: async function (previewMode, widgetValue, params, type) {
        // Never allow previews for theme customizations
        if (previewMode) {
            return;
        }

        switch (type) {
            case 'views':
                await this._customizeWebsiteData(widgetValue, params, true);
                break;
            case 'variable':
                await this._customizeWebsiteVariable(widgetValue, params);
                break;
            case 'color':
                await this._customizeWebsiteColor(widgetValue, params);
                break;
            case 'assets':
                await this._customizeWebsiteData(widgetValue, params, false);
                break;
            default:
                if (params.customCustomization) {
                    await params.customCustomization.call(this, widgetValue, params);
                }
        }

        if (params.reload || params.noBundleReload) {
            // Caller will reload the page, nothing needs to be done anymore.
            return;
        }

        // Finally, only update the bundles as no reload is required
        await this._reloadBundles();
        // TODO kept to be fully stable but this is useless, this is done
        // automatically with _reloadBundles. As this is not a costly operation
        // it is ok to do it twice for no reason in stable. To remove in master.
        this.trigger_up('option_update', {
            optionName: 'ThemeColors',
            name: 'update_color_previews',
        });

        // Some public widgets may depend on the variables that were
        // customized, so we have to restart them *all*.
        await new Promise((resolve, reject) => {
            this.trigger_up('widgets_start_request', {
                editableMode: true,
                onSuccess: () => resolve(),
                onFailure: () => reject(),
            });
        });
    },
    /**
     * @private
     */
    async _customizeWebsiteColor(color, params) {
        await this._customizeWebsiteColors({[params.color]: color}, params);
    },
    /**
     * @private
     */
     async _customizeWebsiteColors(colors, params) {
        colors = colors || {};

        const baseURL = '/website/static/src/scss/options/colors/';
        const colorType = params.colorType ? (params.colorType + '_') : '';
        const url = `${baseURL}user_${colorType}color_palette.scss`;

        const finalColors = {};
        for (const [colorName, color] of Object.entries(colors)) {
            finalColors[colorName] = color;
            if (color) {
                if (weUtils.isColorCombinationName(color)) {
                    finalColors[colorName] = parseInt(color);
                } else if (!ColorpickerWidget.isCSSColor(color)) {
                    finalColors[colorName] = `'${color}'`;
                }
            }
        }
        return this._makeSCSSCusto(url, finalColors, params.nullValue);
    },
    /**
     * @private
     */
    _customizeWebsiteVariable: async function (value, params) {
        return this._makeSCSSCusto('/website/static/src/scss/options/user_values.scss', {
            [params.variable]: value,
        }, params.nullValue);
    },
    /**
     * @private
     */
    async _customizeWebsiteData(value, params, isViewData) {
        const allDataKeys = this._getDataKeysFromPossibleValues(params.possibleValues);
        const enableDataKeys = value.split(/\s*,\s*/);
        const disableDataKeys = allDataKeys.filter(value => !enableDataKeys.includes(value));
        const resetViewArch = !!params.resetViewArch;

        if (params.name === 'header_sidebar_opt') {
            // When the user selects sidebar as header, make sure that the
            // header position is regular.
            // TODO we should avoid having that `if` in the generic option
            // class (maybe simply use data-trigger but the header template
            // option as no associated data-js to hack). To adapt in master.
            await new Promise(resolve => {
                this.trigger_up('action_demand', {
                    actionName: 'toggle_page_option',
                    params: [{name: 'header_overlay', value: false}],
                    onSuccess: () => resolve(),
                });
            });
        }

        return this._rpc({
            route: '/website/theme_customize_data',
            params: {
                'is_view_data': isViewData,
                'enable': enableDataKeys,
                'disable': disableDataKeys,
                'reset_view_arch': resetViewArch,
            },
        });
    },
    /**
     * @private
     */
    _getDataKeysFromPossibleValues(possibleValues) {
        const allDataKeys = [];
        for (const dataKeysStr of possibleValues) {
            allDataKeys.push(...dataKeysStr.split(/\s*,\s*/));
        }
        return allDataKeys.filter((v, i, arr) => arr.indexOf(v) === i);
    },
    /**
     * @private
     * @param {Array} possibleValues
     * @param {Boolean} isViewData true = "ir.ui.view", false = "ir.asset"
     * @returns {String}
     */
    async _getEnabledCustomizeValues(possibleValues, isViewData) {
        const allDataKeys = this._getDataKeysFromPossibleValues(possibleValues);
        const enabledValues = await this._rpc({
            route: '/website/theme_customize_data_get',
            params: {
                'keys': allDataKeys,
                'is_view_data': isViewData,
            },
        });
        let mostValuesStr = '';
        let mostValuesNb = 0;
        for (const valuesStr of possibleValues) {
            const enableValues = valuesStr.split(/\s*,\s*/);
            if (enableValues.length > mostValuesNb
                    && enableValues.every(value => enabledValues.includes(value))) {
                mostValuesStr = valuesStr;
                mostValuesNb = enableValues.length;
            }
        }
        return mostValuesStr; // Need to return the exact same string as in possibleValues
    },
    /**
     * @private
     */
    _makeSCSSCusto: async function (url, values, defaultValue = 'null') {
        return this._rpc({
            model: 'web_editor.assets',
            method: 'make_scss_customization',
            args: [url, _.mapObject(values, v => v || defaultValue)],
        });
    },
    /**
     * Refreshes all public widgets related to the given element.
     *
     * @private
     * @param {jQuery} [$el=this.$target]
     * @returns {Promise}
     */
    _refreshPublicWidgets: async function ($el) {
        return new Promise((resolve, reject) => {
            this.trigger_up('widgets_start_request', {
                editableMode: true,
                $target: $el || this.$target,
                onSuccess: resolve,
                onFailure: reject,
            });
        });
    },
    /**
     * @private
     */
    _reloadBundles: async function() {
        return new Promise((resolve, reject) => {
            this.trigger_up('reload_bundles', {
                onSuccess: () => resolve(),
                onFailure: () => reject(),
            });
        });
    },
    /**
     * @override
     */
    _select: async function (previewMode, widget) {
        await this._super(...arguments);

        if (this.options.isWebsite && !widget.$el.closest('[data-no-widget-refresh="true"]').length) {
            // TODO the flag should be retrieved through widget params somehow
            await this._refreshPublicWidgets();
        }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {OdooEvent} ev
     */
    _onGoogleFontsCustoRequest: function (ev) {
        const values = ev.data.values ? _.clone(ev.data.values) : {};
        const googleFonts = ev.data.googleFonts;
        const googleLocalFonts = ev.data.googleLocalFonts;
        if (googleFonts.length) {
            values['google-fonts'] = "('" + googleFonts.join("', '") + "')";
        } else {
            values['google-fonts'] = 'null';
        }
<<<<<<< HEAD
        if (googleLocalFonts.length) {
=======
        // check undefined, this is a backport, a custo might not pass this key
        if (googleLocalFonts !== undefined && googleLocalFonts.length) {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            values['google-local-fonts'] = "(" + googleLocalFonts.join(", ") + ")";
        } else {
            values['google-local-fonts'] = 'null';
        }
        this.trigger_up('snippet_edition_request', {exec: async () => {
            return this._makeSCSSCusto('/website/static/src/scss/options/user_values.scss', values);
        }});
        this.trigger_up('request_save', {
            reloadEditor: true,
        });
    },
});

function _getLastPreFilterLayerElement($el) {
    // Make sure parallax and video element are considered to be below the
    // color filters / shape
    const $bgVideo = $el.find('> .o_bg_video_container');
    if ($bgVideo.length) {
        return $bgVideo[0];
    }
    const $parallaxEl = $el.find('> .s_parallax_bg');
    if ($parallaxEl.length) {
        return $parallaxEl[0];
    }
    return null;
}

options.registry.BackgroundToggler.include({
    /**
     * Toggles background video on or off.
     *
     * @see this.selectClass for parameters
     */
    toggleBgVideo(previewMode, widgetValue, params) {
        if (!widgetValue) {
            this.$target.find('> .o_we_bg_filter').remove();
            // TODO: use setWidgetValue instead of calling background directly when possible
            const [bgVideoWidget] = this._requestUserValueWidgets('bg_video_opt');
            const bgVideoOpt = bgVideoWidget.getParent();
            return bgVideoOpt._setBgVideo(false, '');
        } else {
            // TODO: use trigger instead of el.click when possible
            this._requestUserValueWidgets('bg_video_opt')[0].el.click();
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeWidgetState(methodName, params) {
        if (methodName === 'toggleBgVideo') {
            return this.$target[0].classList.contains('o_background_video');
        }
        return this._super(...arguments);
    },
    /**
     * TODO an overall better management of background layers is needed
     *
     * @override
     */
    _getLastPreFilterLayerElement() {
        const el = _getLastPreFilterLayerElement(this.$target);
        if (el) {
            return el;
        }
        return this._super(...arguments);
    },
});

options.registry.BackgroundShape.include({
    /**
     * TODO need a better management of background layers
     *
     * @override
     */
    _getLastPreShapeLayerElement() {
        const el = this._super(...arguments);
        if (el) {
            return el;
        }
        return _getLastPreFilterLayerElement(this.$target);
    },
    /**
     * @override
     */
    _removeShapeEl(shapeEl) {
        this.trigger_up('widgets_stop_request', {
            $target: $(shapeEl),
        });
        return this._super(...arguments);
    },
<<<<<<< HEAD
});

options.registry.ReplaceMedia.include({
    /**
     * Adds an anchor to the url.
     * Here "anchor" means a specific section of a page.
     *
     * @see this.selectClass for parameters
     */
    setAnchor(previewMode, widgetValue, params) {
        const linkEl = this.$target[0].parentElement;
        let url = linkEl.getAttribute('href');
        url = url.split('#')[0];
        linkEl.setAttribute('href', url + widgetValue);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeWidgetState(methodName, params) {
        if (methodName === 'setAnchor') {
            const parentEl = this.$target[0].parentElement;
            if (parentEl.tagName === 'A') {
                const href = parentEl.getAttribute('href') || '';
                return href ? `#${href.split('#')[1]}` : '';
            }
            return '';
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    async _computeWidgetVisibility(widgetName, params) {
        if (widgetName === 'media_link_anchor_opt') {
            const parentEl = this.$target[0].parentElement;
            const linkEl = parentEl.tagName === 'A' ? parentEl : null;
            const href = linkEl ? linkEl.getAttribute('href') : false;
            return href && href.startsWith('/');
        }
        return this._super(...arguments);
    },
    /**
     * Fills the dropdown with the available anchors for the page referenced in
     * the href.
     *
     * @override
     */
    async _renderCustomXML(uiFragment) {
        if (!this.options.isWebsite) {
            return this._super(...arguments);
        }
        await this._super(...arguments);



        const oldURLWidgetEl = uiFragment.querySelector('[data-name="media_url_opt"]');

        const URLWidgetEl = document.createElement('we-urlpicker');
        // Copy attributes
        for (const {name, value} of oldURLWidgetEl.attributes) {
            URLWidgetEl.setAttribute(name, value);
        }
        URLWidgetEl.title = _t("Hint: Type '/' to search an existing page and '#' to link to an anchor.");
        oldURLWidgetEl.replaceWith(URLWidgetEl);

        const hrefValue = this.$target[0].parentElement.getAttribute('href');
        if (!hrefValue || !hrefValue.startsWith('/')) {
            return;
        }
        const urlWithoutAnchor = hrefValue.split('#')[0];
        const selectEl = document.createElement('we-select');
        selectEl.dataset.name = 'media_link_anchor_opt';
        selectEl.dataset.dependencies = 'media_url_opt';
        selectEl.dataset.noPreview = 'true';
        selectEl.classList.add('o_we_sublevel_1');
        selectEl.setAttribute('string', _t("Page Anchor"));
        const anchors = await wUtils.loadAnchors(urlWithoutAnchor);
        for (const anchor of anchors) {
            const weButtonEl = document.createElement('we-button');
            weButtonEl.dataset.setAnchor = anchor;
            weButtonEl.textContent = anchor;
            selectEl.append(weButtonEl);
        }
        URLWidgetEl.after(selectEl);
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
});

options.registry.BackgroundVideo = options.Class.extend({

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * Sets the target's background video.
     *
     * @see this.selectClass for parameters
     */
    background: function (previewMode, widgetValue, params) {
        if (previewMode === 'reset' && this.videoSrc) {
            return this._setBgVideo(false, this.videoSrc);
        }
        return this._setBgVideo(previewMode, widgetValue);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeWidgetState: function (methodName, params) {
        if (methodName === 'background') {
            if (this.$target[0].classList.contains('o_background_video')) {
                return this.$('> .o_bg_video_container iframe').attr('src');
            }
            return '';
        }
        return this._super(...arguments);
    },
    /**
     * Updates the background video used by the snippet.
     *
     * @private
     * @see this.selectClass for parameters
     * @returns {Promise}
     */
    _setBgVideo: async function (previewMode, value) {
        this.$('> .o_bg_video_container').toggleClass('d-none', previewMode === true);

        if (previewMode !== false) {
            return;
        }

        this.videoSrc = value;
        var target = this.$target[0];
        target.classList.toggle('o_background_video', !!(value && value.length));
        if (value && value.length) {
            target.dataset.bgVideoSrc = value;
        } else {
            delete target.dataset.bgVideoSrc;
        }
        await this._refreshPublicWidgets();
    },
});

options.registry.OptionsTab = options.Class.extend({
    GRAY_PARAMS: {EXTRA_SATURATION: "gray-extra-saturation", HUE: "gray-hue"},

    /**
     * @override
     */
    init() {
        this._super(...arguments);
        this.grayParams = {};
        this.grays = {};
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async updateUI() {
        // The bg-XXX classes have been updated (and could be updated by another
        // option like changing color palette) -> update the preview element.
        const ownerDocument = this.$target[0].ownerDocument;
        const style = ownerDocument.defaultView.getComputedStyle(ownerDocument.documentElement);
        const grayPreviewEls = this.$el.find(".o_we_gray_preview span");
        for (const e of grayPreviewEls) {
            const bgValue = weUtils.getCSSVariableValue(e.getAttribute('variable'), style);
            e.style.setProperty("background-color", bgValue, "important");
        }

        // If the gray palette has been generated by Odoo standard option,
        // the hue of all gray is the same and the saturation has been
        // increased/decreased by the same amount for all grays in
        // comparaison with BS grays. However the system supports any
        // gray palette.

        const hues = [];
        const saturationDiffs = [];
        let oneHasNoSaturation = false;
        const baseStyle = getComputedStyle(document.documentElement);
        for (let id = 100; id <= 900; id += 100) {
            const gray = weUtils.getCSSVariableValue(`${id}`, style);
            const grayRGB = ColorpickerWidget.convertCSSColorToRgba(gray);
            const grayHSL = ColorpickerWidget.convertRgbToHsl(grayRGB.red, grayRGB.green, grayRGB.blue);

            const baseGray = weUtils.getCSSVariableValue(`base-${id}`, baseStyle);
            const baseGrayRGB = ColorpickerWidget.convertCSSColorToRgba(baseGray);
            const baseGrayHSL = ColorpickerWidget.convertRgbToHsl(baseGrayRGB.red, baseGrayRGB.green, baseGrayRGB.blue);

            if (grayHSL.saturation > 0.01) {
                if (grayHSL.lightness > 0.01 && grayHSL.lightness < 99.99) {
                    hues.push(grayHSL.hue);
                }
                if (grayHSL.saturation < 99.99) {
                    saturationDiffs.push(grayHSL.saturation - baseGrayHSL.saturation);
                }
            } else {
                oneHasNoSaturation = true;
            }
        }
        this.grayHueIsDefined = !!hues.length;

        // Average of angles: we need to take the average of found hues
        // because even if grays are supposed to be set to the exact
        // same hue by the Odoo editor, there might be rounding errors
        // during the conversion from RGB to HSL as the HSL system
        // allows to represent more colors that the RGB hexadecimal
        // notation (also: hue 360 = hue 0 and should not be averaged to 180).
        // This also better support random gray palettes.
        this.grayParams[this.GRAY_PARAMS.HUE] = (!hues.length) ? 0 : Math.round((Math.atan2(
            hues.map(hue => Math.sin(hue * Math.PI / 180)).reduce((memo, value) => memo + value, 0) / hues.length,
            hues.map(hue => Math.cos(hue * Math.PI / 180)).reduce((memo, value) => memo + value, 0) / hues.length
        ) * 180 / Math.PI) + 360) % 360;

        // Average of found saturation diffs, or all grays have no
        // saturation, or all grays are fully saturated.
        this.grayParams[this.GRAY_PARAMS.EXTRA_SATURATION] = saturationDiffs.length
            ? saturationDiffs.reduce((memo, value) => memo + value, 0) / saturationDiffs.length
            : (oneHasNoSaturation ? -100 : 100);

        await this._super(...arguments);
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async customizeGray(previewMode, widgetValue, params) {
        // Gray parameters are used *on the JS side* to compute the grays that
        // will be saved in the database. We indeed need those grays to be
        // computed here for faster previews so this allows to not duplicate
        // most of the logic. Also, this gives flexibility to maybe allow full
        // customization of grays in custo and themes. Also, this allows to ease
        // migration if the computation here was to change: the user grays would
        // still be unchanged as saved in the database.

        this.grayParams[params.param] = parseInt(widgetValue);
        for (let i = 1; i < 10; i++) {
            const key = (100 * i).toString();
            this.grays[key] = this._buildGray(key);
        }

        // Preview UI update
        this.$el.find(".o_we_gray_preview").each((_, e) => {
            e.style.setProperty("background-color", this.grays[e.getAttribute('variable')], "important");
        });

        // Save all computed (JS side) grays in database
        await this._customizeWebsite(previewMode, undefined, Object.assign({}, params, {
            customCustomization: () => { // TODO this could be prettier
                return this._customizeWebsiteColors(this.grays, Object.assign({}, params, {
                    colorType: 'gray',
                }));
            },
        }));
    },
    /**
     * @see this.selectClass for parameters
     */
    async configureApiKey(previewMode, widgetValue, params) {
        return new Promise(resolve => {
            this.trigger_up('gmap_api_key_request', {
                editableMode: true,
                reconfigure: true,
                onSuccess: () => resolve(),
            });
        });
    },
    /**
     * @see this.selectClass for parameters
     */
    async customizeBodyBgType(previewMode, widgetValue, params) {
        if (widgetValue === 'NONE') {
            this.bodyImageType = 'image';
            return this.customizeBodyBg(previewMode, '', params);
        }
        // TODO improve: hack to click on external image picker
        this.bodyImageType = widgetValue;
        const widget = this._requestUserValueWidgets(params.imagepicker)[0];
        widget.enable();
    },
    /**
     * @override
     */
    async customizeBodyBg(previewMode, widgetValue, params) {
        // TODO improve: customize two variables at the same time...
        await this.customizeWebsiteVariable(previewMode, this.bodyImageType, {variable: 'body-image-type'});
        await this.customizeWebsiteVariable(previewMode, widgetValue ? `'${widgetValue}'` : '', {variable: 'body-image'});
    },
    /**
     * @see this.selectClass for parameters
     */
    async openCustomCodeDialog(previewMode, widgetValue, params) {
        const libsProm = loadBundle({
            jsLibs: [
                '/web/static/lib/ace/ace.js',
                '/web/static/lib/ace/mode-xml.js',
                '/web/static/lib/ace/mode-qweb.js',
            ],
        });

        let websiteId;
        this.trigger_up('context_get', {
            callback: (ctx) => {
                websiteId = ctx['website_id'];
            },
        });

        let website;
        const dataProm = this._rpc({
            model: 'website',
            method: 'read',
            args: [[websiteId], ['custom_code_head', 'custom_code_footer']],
        }).then(websites => {
            website = websites[0];
        });

        let fieldName, title, contentText;
        if (widgetValue === 'head') {
            fieldName = 'custom_code_head';
            title = _t('Custom head code');
            contentText = _t('Enter code that will be added into the <head> of every page of your site.');
        } else {
            fieldName = 'custom_code_footer';
            title = _t('Custom end of body code');
            contentText = _t('Enter code that will be added before the </body> of every page of your site.');
        }

        await Promise.all([libsProm, dataProm]);

        await new Promise(resolve => {
            const $content = $(core.qweb.render('website.custom_code_dialog_content', {
                contentText,
            }));
            const aceEditor = this._renderAceEditor($content.find('.o_ace_editor_container')[0], website[fieldName] || '');
            const dialog = new Dialog(this, {
                title,
                $content,
                buttons: [
                    {
                        text: _t("Save"),
                        classes: 'btn-primary',
                        click: async () => {
                            await this._rpc({
                                model: 'website',
                                method: 'write',
                                args: [
                                    [websiteId],
                                    {[fieldName]: aceEditor.getValue()},
                                ],
                            });
                        },
                        close: true,
                    },
                    {
                        text: _t("Discard"),
                        close: true,
                    },
                ],
            });
            dialog.on('closed', this, resolve);
            dialog.open();
        });
    },
    /**
     * @see this.selectClass for parameters
     */
    async switchTheme(previewMode, widgetValue, params) {
        const save = await new Promise(resolve => {
            Dialog.confirm(this, _t("Changing theme requires to leave the editor. This will save all your changes, are you sure you want to proceed? Be careful that changing the theme will reset all your color customizations."), {
                confirm_callback: () => resolve(true),
                cancel_callback: () => resolve(false),
            });
        });
        if (!save) {
            return;
        }
        this.trigger_up('request_save', {
            reload: false,
            action: 'website.theme_install_kanban_action',
        });
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {String} id
     * @returns {String} the adjusted color of gray
     */
    _buildGray(id) {
        // Getting base grays defined in color_palette.scss
        const gray = weUtils.getCSSVariableValue(`base-${id}`, getComputedStyle(document.documentElement));
        const grayRGB = ColorpickerWidget.convertCSSColorToRgba(gray);
        const hsl = ColorpickerWidget.convertRgbToHsl(grayRGB.red, grayRGB.green, grayRGB.blue);
        const adjustedGrayRGB = ColorpickerWidget.convertHslToRgb(this.grayParams[this.GRAY_PARAMS.HUE],
            Math.min(Math.max(hsl.saturation + this.grayParams[this.GRAY_PARAMS.EXTRA_SATURATION], 0), 100),
            hsl.lightness);
        return ColorpickerWidget.convertRgbaToCSSColor(adjustedGrayRGB.red, adjustedGrayRGB.green, adjustedGrayRGB.blue);
    },
    /**
     * @override
     */
    async _renderCustomXML(uiFragment) {
        await this._super(...arguments);
        const extraSaturationRangeEl = uiFragment.querySelector(`we-range[data-param=${this.GRAY_PARAMS.EXTRA_SATURATION}]`);
        if (extraSaturationRangeEl) {
            const baseGrays = _.range(100, 1000, 100).map(id => {
                const gray = weUtils.getCSSVariableValue(`base-${id}`);
                const grayRGB = ColorpickerWidget.convertCSSColorToRgba(gray);
                const hsl = ColorpickerWidget.convertRgbToHsl(grayRGB.red, grayRGB.green, grayRGB.blue);
                return {id: id, hsl: hsl};
            });
            const first = baseGrays[0];
            const maxValue = baseGrays.reduce((gray, value) => {
                return gray.hsl.saturation > value.hsl.saturation ? gray : value;
            }, first);
            const minValue = baseGrays.reduce((gray, value) => {
                return gray.hsl.saturation < value.hsl.saturation ? gray : value;
            }, first);
            extraSaturationRangeEl.dataset.max = 100 - minValue.hsl.saturation;
            extraSaturationRangeEl.dataset.min = -maxValue.hsl.saturation;
        }
        uiFragment.querySelectorAll('we-colorpicker').forEach(el => {
            el.dataset.lazyPalette = 'true';
        });
    },
    /**
     * @override
     */
    async _checkIfWidgetsUpdateNeedWarning(widgets) {
        const warningMessage = await this._super(...arguments);
        if (warningMessage) {
            return warningMessage;
        }
        for (const widget of widgets) {
            if (widget.getMethodsNames().includes('customizeWebsiteVariable')
                    && widget.getMethodsParams('customizeWebsiteVariable').variable === 'color-palettes-name') {
                const hasCustomizedColors = weUtils.getCSSVariableValue('has-customized-colors');
                if (hasCustomizedColors && hasCustomizedColors !== 'false') {
                    return _t("Changing the color palette will reset all your color customizations, are you sure you want to proceed?");
                }
            }
        }
        return '';
    },
    /**
     * @override
     */
    async _computeWidgetState(methodName, params) {
        if (methodName === 'customizeBodyBgType') {
<<<<<<< HEAD
            const bgImage = getComputedStyle(this.ownerDocument.querySelector('#wrapwrap'))['background-image'];
=======
            const bgImage = $('#wrapwrap').css('background-image');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            if (bgImage === 'none') {
                return "NONE";
            }
            return weUtils.getCSSVariableValue('body-image-type');
<<<<<<< HEAD
        }
        if (methodName === 'customizeGray') {
            // See updateUI override
            return this.grayParams[params.param];
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    async _computeWidgetVisibility(widgetName, params) {
        if (widgetName === 'body_bg_image_opt') {
            return false;
        }
        if (params.param === this.GRAY_PARAMS.HUE) {
            return this.grayHueIsDefined;
        }
        return this._super(...arguments);
    },
    /**
     * @private
     * @param {DOMElement} node
     * @param {String} content text of the editor
     * @returns {Object}
     */
    _renderAceEditor(node, content) {
        const aceEditor = window.ace.edit(node);
        aceEditor.setTheme('ace/theme/monokai');
        aceEditor.setValue(content, 1);
        aceEditor.setOptions({
            minLines: 20,
            maxLines: Infinity,
            showPrintMargin: false,
        });
        aceEditor.renderer.setOptions({
            highlightGutterLine: true,
            showInvisibles: true,
            fontSize: 14,
        });

        const aceSession = aceEditor.getSession();
        aceSession.setOptions({
            mode: "ace/mode/qweb",
            useWorker: false,
        });
        return aceEditor;
    },
    /**
     * @override
     */
    async _renderCustomXML(uiFragment) {
        uiFragment.querySelectorAll('we-colorpicker').forEach(el => {
            el.dataset.lazyPalette = 'true';
        });
    },
});

options.registry.ThemeColors = options.registry.OptionsTab.extend({
    /**
     * @override
     */
    async start() {
        // Checks for support of the old color system
        const style = window.getComputedStyle(this.$target[0].ownerDocument.documentElement);
        const supportOldColorSystem = weUtils.getCSSVariableValue('support-13-0-color-system', style) === 'true';
        const hasCustomizedOldColorSystem = weUtils.getCSSVariableValue('has-customized-13-0-color-system', style) === 'true';
        this._showOldColorSystemWarning = supportOldColorSystem && hasCustomizedOldColorSystem;

        return this._super(...arguments);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    notify(name, data) {
        if (name === 'update_color_previews') {
            // TODO remove this part in master, this is handled automatically
            // at each bundle reload.
            this.updateColorPreviews = true;
        }
    },
    /**
     * @override
     */
    async updateUIVisibility() {
        await this._super(...arguments);
        const oldColorSystemEl = this.el.querySelector('.o_old_color_system_warning');
        oldColorSystemEl.classList.toggle('d-none', !this._showOldColorSystemWarning);
    },
    /**
     * @override
     */
    async updateUI() {
        if (this.updateColorPreviews) {
            // TODO remove this part in master, this is handled automatically
            // at each bundle reload.
            this.trigger_up('update_color_previews');
            this.updateColorPreviews = false;
        }
        await this._super(...arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
<<<<<<< HEAD
    _select() {
        this.updateColorPreviews = true;
        return this._super(...arguments);
    },
    /**
     * @override
     */
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    async _renderCustomXML(uiFragment) {
        const paletteSelectorEl = uiFragment.querySelector('[data-variable="color-palettes-name"]');
        const style = window.getComputedStyle(document.documentElement);
        const allPaletteNames = weUtils.getCSSVariableValue('palette-names', style).split(', ').map((name) => {
            return name.replace(/'/g, "");
        });
        for (const paletteName of allPaletteNames) {
            const btnEl = document.createElement('we-button');
            btnEl.classList.add('o_palette_color_preview_button');
            btnEl.dataset.customizeWebsiteVariable = `'${paletteName}'`;
            [1, 3, 2].forEach(c => {
                const colorPreviewEl = document.createElement('span');
                colorPreviewEl.classList.add('o_palette_color_preview');
                const color = weUtils.getCSSVariableValue(`o-palette-${paletteName}-o-color-${c}`, style);
                colorPreviewEl.style.backgroundColor = color;
                btnEl.appendChild(colorPreviewEl);
            });
            paletteSelectorEl.appendChild(btnEl);
        }

<<<<<<< HEAD
        const presetCollapseEl = uiFragment.querySelector('we-collapse.o_we_theme_presets_collapse');
        let ccPreviewEls = [];
        for (let i = 1; i <= 5; i++) {
            const collapseEl = document.createElement('we-collapse');
            const ccPreviewEl = $(qweb.render('web_editor.color.combination.preview'))[0];
            ccPreviewEl.classList.add('text-center', `o_cc${i}`, 'o_colored_level', 'o_we_collapse_toggler');
=======
        for (let i = 1; i <= 5; i++) {
            const collapseEl = document.createElement('we-collapse');
            const ccPreviewEl = $(qweb.render('web_editor.color.combination.preview'))[0];
            ccPreviewEl.classList.add('text-center', `o_cc${i}`);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            collapseEl.appendChild(ccPreviewEl);
            const editionEls = $(qweb.render('website.color_combination_edition', {number: i}));
            for (const el of editionEls) {
                collapseEl.appendChild(el);
            }
<<<<<<< HEAD
            ccPreviewEls.push(ccPreviewEl);
            presetCollapseEl.appendChild(collapseEl);
        }
        // TODO investigate in master why this would be necessary
        this.trigger_up('update_color_previews');
=======
            uiFragment.appendChild(collapseEl);
        }

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        await this._super(...arguments);
    },
});

options.registry.menu_data = options.Class.extend({
    /**
<<<<<<< HEAD
     * When the users selects a menu, a popover is shown with 4 possible
     * actions: follow the link in a new tab, copy the menu link, edit the menu,
     * or edit the menu tree.
     * The popover shows a preview of the menu link. Remote URL only show the
     * favicon.
     *
     * @override
     */
    start: function () {
        const wysiwyg = $(this.ownerDocument.getElementById('wrapwrap')).data('wysiwyg');
        const popoverContainer = this.ownerDocument.getElementById('oe_manipulators');
        wLinkPopoverWidget.createFor(this, this.$target[0], { wysiwyg, container: popoverContainer });
        return this._super(...arguments);
    },
    /**
      * When the users selects another element on the page, makes sure the
      * popover is closed.
      *
      * @override
      */
    onBlur: function () {
        this.$target.popover('hide');
=======
     * @override
     */
    async start() {
        await this._super(...arguments);
        this.isWebsiteDesigner = await this._rpc({
            'model': 'res.users',
            'method': 'has_group',
            'args': ['website.group_website_designer'],
        });
    },
    /**
     * When the users selects a menu, a dialog is opened to ask him if he wants
     * to follow the link (and leave editor), edit the menu or do nothing.
     *
     * @override
     */
    onFocus: function () {
        var self = this;
        const buttons = [
            {
                text: _t("Go to Link"), classes: 'btn-primary', click: function () {
                    self.trigger_up('request_save', {
                        reload: false,
                        onSuccess: function () {
                            window.location.href = self.$target.attr('href');
                        },
                    });
                },
            },
        ];
        if (this.isWebsiteDesigner) {
            buttons.push({
                text: _t("Edit the menu"), classes: 'btn-primary', click: function () {
                    this.trigger_up('action_demand', {
                        actionName: 'edit_menu',
                        params: [
                            function () {
                                var prom = new Promise(function (resolve, reject) {
                                    self.trigger_up('request_save', {
                                        onSuccess: resolve,
                                        onFailure: reject,
                                    });
                                });
                                return prom;
                            },
                        ],
                    });
                },
            });
        }
        buttons.push({text: _t("Stay on this page"), close: true});

        (new Dialog(this, {
            title: _t("Confirmation"),
            $content: $(core.qweb.render('website.leaving_current_page_edition')),
            buttons: buttons,
        })).open();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
});

options.registry.company_data = options.Class.extend({
    /**
     * Fetches data to determine the URL where the user can edit its company
     * data. Saves the info in the prototype to do this only once.
     *
     * @override
     */
    start: function () {
        var proto = options.registry.company_data.prototype;
        var prom;
        var self = this;
        if (proto.__link === undefined) {
            prom = this._rpc({route: '/web/session/get_session_info'}).then(function (session) {
                return self._rpc({
                    model: 'res.users',
                    method: 'read',
                    args: [session.uid, ['company_id']],
                });
            }).then(function (res) {
                proto.__link = '/web#action=base.action_res_company_form&view_type=form&id=' + encodeURIComponent(res && res[0] && res[0].company_id[0] || 1);
            });
        }
        return Promise.all([this._super.apply(this, arguments), prom]);
    },
    /**
     * When the users selects company data, opens a dialog to ask him if he
     * wants to be redirected to the company form view to edit it.
     *
     * @override
     */
    onFocus: function () {
        var self = this;
        var proto = options.registry.company_data.prototype;

        Dialog.confirm(this, _t("Do you want to edit the company data ?"), {
            confirm_callback: function () {
                self.trigger_up('request_save', {
                    reload: false,
                    onSuccess: function () {
                        window.location.href = proto.__link;
                    },
                });
            },
        });
    },
});

options.registry.Carousel = options.Class.extend({
    /**
     * @override
     */
    start: function () {
        this.$bsTarget.carousel('pause');
        this.$indicators = this.$target.find('.carousel-indicators');
        this.$controls = this.$target.find('.carousel-control-prev, .carousel-control-next, .carousel-indicators');

        // Prevent enabling the carousel overlay when clicking on the carousel
        // controls (indeed we want it to change the carousel slide then enable
        // the slide overlay) + See "CarouselItem" option.
        this.$controls.addClass('o_we_no_overlay');

        let _slideTimestamp;
        this.$bsTarget.on('slide.bs.carousel.carousel_option', () => {
            _slideTimestamp = window.performance.now();
            setTimeout(() => this.trigger_up('hide_overlay'));
        });
        this.$bsTarget.on('slid.bs.carousel.carousel_option', () => {
            // slid.bs.carousel is most of the time fired too soon by bootstrap
            // since it emulates the transitionEnd with a setTimeout. We wait
            // here an extra 20% of the time before retargeting edition, which
            // should be enough...
            const _slideDuration = (window.performance.now() - _slideTimestamp);
            setTimeout(() => {
                this.trigger_up('activate_snippet', {
                    $snippet: this.$target.find('.carousel-item.active'),
                    ifInactiveOptions: true,
                });
                this.$bsTarget.trigger('active_slide_targeted');
            }, 0.2 * _slideDuration);
        });

        return this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    destroy: function () {
        this._super.apply(this, arguments);
        this.$bsTarget.off('.carousel_option');
    },
    /**
     * @override
     */
    onBuilt: function () {
        this._assignUniqueID();
    },
    /**
     * @override
     */
    onClone: function () {
        this._assignUniqueID();
    },
    /**
     * @override
     */
    cleanForSave: function () {
        const $items = this.$target.find('.carousel-item');
        $items.removeClass('next prev left right active').first().addClass('active');
        this.$indicators.find('li').removeClass('active').empty().first().addClass('active');
    },
    /**
     * @override
     */
    notify: function (name, data) {
        this._super(...arguments);
        if (name === 'add_slide') {
            this._addSlide();
        }
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @see this.selectClass for parameters
     */
    addSlide(previewMode, widgetValue, params) {
        this._addSlide();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Creates a unique ID for the carousel and reassign data-attributes that
     * depend on it.
     *
     * @private
     */
    _assignUniqueID: function () {
        const id = 'myCarousel' + Date.now();
        this.$target.attr('id', id);
        this.$target.find('[data-bs-target]').attr('data-bs-target', '#' + id);
        _.each(this.$target.find('[data-bs-slide], [data-bs-slide-to]'), function (el) {
            var $el = $(el);
            if ($el.attr('data-bs-target')) {
                $el.attr('data-bs-target', '#' + id);
            } else if ($el.attr('href')) {
                $el.attr('href', '#' + id);
            }
        });
    },
    /**
     * Adds a slide.
     *
     * @private
     */
    _addSlide() {
        const $items = this.$target.find('.carousel-item');
        this.$controls.removeClass('d-none');
        const $active = $items.filter('.active');
        this.$indicators.append($('<li>', {
            'data-bs-target': '#' + this.$target.attr('id'),
            'data-bs-slide-to': $items.length,
        }));
        this.$indicators.append(' ');
        // Need to remove editor data from the clone so it gets its own.
        $active.clone(false)
            .removeClass('active')
            .insertAfter($active);
        this.$bsTarget.carousel('next');
    },
});

options.registry.CarouselItem = options.Class.extend({
    isTopOption: true,
    forceNoDeleteButton: true,

    /**
     * @override
     */
    start: function () {
        this.$carousel = this.$bsTarget.closest('.carousel');
        this.$indicators = this.$carousel.find('.carousel-indicators');
        this.$controls = this.$carousel.find('.carousel-control-prev, .carousel-control-next, .carousel-indicators');

        var leftPanelEl = this.$overlay.data('$optionsSection')[0];
        var titleTextEl = leftPanelEl.querySelector('we-title > span');
        this.counterEl = document.createElement('span');
        titleTextEl.appendChild(this.counterEl);

        return this._super(...arguments);
    },
    /**
     * @override
     */
    destroy: function () {
        this._super(...arguments);
        this.$carousel.off('.carousel_item_option');
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Updates the slide counter.
     *
     * @override
     */
    updateUI: async function () {
        await this._super(...arguments);
        const $items = this.$carousel.find('.carousel-item');
        const $activeSlide = $items.filter('.active');
        const updatedText = ` (${$activeSlide.index() + 1}/${$items.length})`;
        this.counterEl.textContent = updatedText;
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @see this.selectClass for parameters
     */
<<<<<<< HEAD
    addSlideItem(previewMode, widgetValue, params) {
        this.trigger_up('option_update', {
            optionName: 'Carousel',
            name: 'add_slide',
        });
=======
    addSlide: function (previewMode) {
        const $items = this.$carousel.find('.carousel-item');
        this.$controls.removeClass('d-none');
        this.$indicators.append($('<li>', {
            'data-target': '#' + this.$carousel.attr('id'),
            'data-slide-to': $items.length,
        }));
        this.$indicators.append(' ');
        // Need to remove editor data from the clone so it gets its own.
        const $active = $items.filter('.active');
        $active.clone(false)
            .removeClass('active')
            .insertAfter($active);
        this.$carousel.carousel('next');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    /**
     * Removes the current slide.
     *
     * @see this.selectClass for parameters.
     */
    removeSlide: function (previewMode) {
        const $items = this.$carousel.find('.carousel-item');
        const newLength = $items.length - 1;
        if (!this.removing && newLength > 0) {
            // The active indicator is deleted to ensure that the other
            // indicators will still work after the deletion.
            const $toDelete = $items.filter('.active').add(this.$indicators.find('.active'));
            this.$carousel.one('active_slide_targeted.carousel_item_option', () => {
                $toDelete.remove();
                // To ensure the proper functioning of the indicators, their
                // attributes must reflect the position of the slides.
                const indicatorsEls = this.$indicators[0].querySelectorAll('li');
                for (let i = 0; i < indicatorsEls.length; i++) {
<<<<<<< HEAD
                    indicatorsEls[i].setAttribute('data-bs-slide-to', i);
=======
                    indicatorsEls[i].setAttribute('data-slide-to', i);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                }
                this.$controls.toggleClass('d-none', newLength === 1);
                this.$carousel.trigger('content_changed');
                this.removing = false;
            });
            this.removing = true;
            this.$carousel.carousel('prev');
        }
    },
    /**
     * Goes to next slide or previous slide.
     *
     * @see this.selectClass for parameters
     */
    switchToSlide: function (previewMode, widgetValue, params) {
        switch (widgetValue) {
            case 'left':
                this.$controls.filter('.carousel-control-prev')[0].click();
                break;
            case 'right':
                this.$controls.filter('.carousel-control-next')[0].click();
                break;
        }
    },
});

<<<<<<< HEAD
=======
options.registry.sizing_x = options.registry.sizing.extend({
    /**
     * @override
     */
    onClone: function (options) {
        this._super.apply(this, arguments);
        // Below condition is added to remove offset of target element only
        // and not its children to avoid design alteration of a container/block.
        if (options.isCurrent) {
            var _class = this.$target.attr('class').replace(/\s*(offset-xl-|offset-lg-)([0-9-]+)/g, '');
            this.$target.attr('class', _class);
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _getSize: function () {
        var width = this.$target.closest('.row').width();
        var gridE = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
        var gridW = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
        this.grid = {
            e: [_.map(gridE, v => ('col-lg-' + v)), _.map(gridE, v => width / 12 * v), 'width'],
            w: [_.map(gridW, v => ('offset-lg-' + v)), _.map(gridW, v => width / 12 * v), 'margin-left'],
        };
        return this.grid;
    },
    /**
     * @override
     */
    _onResize: function (compass, beginClass, current) {
        if (compass === 'w' || compass === 'e') {
            const beginOffset = Number(beginClass.match(/offset-lg-([0-9-]+)|$/)[1] || beginClass.match(/offset-xl-([0-9-]+)|$/)[1] || 0);

            if (compass === 'w') {
                // don't change the right border position when we change the offset (replace col size)
                var beginCol = Number(beginClass.match(/col-lg-([0-9]+)|$/)[1] || 0);
                var offset = Number(this.grid.w[0][current].match(/offset-lg-([0-9-]+)|$/)[1] || 0);
                if (offset < 0) {
                    offset = 0;
                }
                var colSize = beginCol - (offset - beginOffset);
                if (colSize <= 0) {
                    colSize = 1;
                    offset = beginOffset + beginCol - 1;
                }
                this.$target.attr('class', this.$target.attr('class').replace(/\s*(offset-xl-|offset-lg-|col-lg-)([0-9-]+)/g, ''));

                this.$target.addClass('col-lg-' + (colSize > 12 ? 12 : colSize));
                if (offset > 0) {
                    this.$target.addClass('offset-lg-' + offset);
                }
            } else if (beginOffset > 0) {
                const endCol = Number(this.grid.e[0][current].match(/col-lg-([0-9]+)|$/)[1] || 0);
                // Avoids overflowing the grid to the right if the
                // column size + the offset exceeds 12.
                if ((endCol + beginOffset) > 12) {
                    this.$target[0].className = this.$target[0].className.replace(/\s*(col-lg-)([0-9-]+)/g, '');
                    this.$target[0].classList.add('col-lg-' + (12 - beginOffset));
                }
            }
        }
        this._super.apply(this, arguments);
    },
});

options.registry.layout_column = options.Class.extend({

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * Changes the number of columns.
     *
     * @see this.selectClass for parameters
     */
    selectCount: async function (previewMode, widgetValue, params) {
        const previousNbColumns = this.$('> .row').children().length;
        let $row = this.$('> .row');
        if (!$row.length) {
            $row = this.$target.contents().wrapAll($('<div class="row"><div class="col-lg-12"/></div>')).parent().parent();
        }

        const nbColumns = parseInt(widgetValue);
        await this._updateColumnCount($row, (nbColumns || 1) - $row.children().length);
        // Yield UI thread to wait for event to bubble before activate_snippet is called.
        // In this case this lets the select handle the click event before we switch snippet.
        // TODO: make this more generic in activate_snippet event handler.
        await new Promise(resolve => setTimeout(resolve));
        if (nbColumns === 0) {
            $row.contents().unwrap().contents().unwrap();
            this.trigger_up('activate_snippet', {$snippet: this.$target});
        } else if (previousNbColumns === 0) {
            this.trigger_up('activate_snippet', {$snippet: this.$('> .row').children().first()});
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeWidgetState: function (methodName, params) {
        if (methodName === 'selectCount') {
            return this.$('> .row').children().length;
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    _computeWidgetVisibility(widgetName, params) {
        if (widgetName === 'zero_cols_opt') {
            // Note: "s_allow_columns" indicates containers which may have
            // bare content (without columns) and are allowed to have columns.
            // By extension, we only show the "None" option on elements that
            // were marked as such as they were allowed to have bare content in
            // the first place.
            return this.$target.is('.s_allow_columns');
        }
        return this._super(...arguments);
    },
    /**
     * Adds new columns which are clones of the last column or removes the
     * last x columns.
     *
     * @private
     * @param {jQuery} $row - the row in which to update the columns
     * @param {integer} count - positif to add, negative to remove
     */
    _updateColumnCount: async function ($row, count) {
        if (!count) {
            return;
        }

        if (count > 0) {
            var $lastColumn = $row.children().last();
            for (var i = 0; i < count; i++) {
                await new Promise(resolve => {
                    this.trigger_up('clone_snippet', {$snippet: $lastColumn, onSuccess: resolve});
                });
            }
        } else {
            var self = this;
            for (const el of $row.children().slice(count)) {
                await new Promise(resolve => {
                    self.trigger_up('remove_snippet', {$snippet: $(el), onSuccess: resolve});
                });
            }
        }

        this._resizeColumns($row.children());
        this.trigger_up('cover_update');
    },
    /**
     * Resizes the columns so that they are kept on one row.
     *
     * @private
     * @param {jQuery} $columns - the columns to resize
     */
    _resizeColumns: function ($columns) {
        const colsLength = $columns.length;
        var colSize = Math.floor(12 / colsLength) || 1;
        var colOffset = Math.floor((12 - colSize * colsLength) / 2);
        var colClass = 'col-lg-' + colSize;
        _.each($columns, function (column) {
            var $column = $(column);
            $column.attr('class', $column.attr('class').replace(/\b(col|offset)-lg(-\d+)?\b/g, ''));
            $column.addClass(colClass);
        });
        if (colOffset) {
            $columns.first().addClass('offset-lg-' + colOffset);
        }
    },
});

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
options.registry.Parallax = options.Class.extend({
    /**
     * @override
     */
    async start() {
        this.parallaxEl = this.$target.find('> .s_parallax_bg')[0] || null;
        this._updateBackgroundOptions();

        this.$target.on('content_changed.ParallaxOption', this._onExternalUpdate.bind(this));

        return this._super(...arguments);
    },
    /**
     * @override
     */
    onFocus() {
        // Refresh the parallax animation on focus; at least useful because
        // there may have been changes in the page that influenced the parallax
        // rendering (new snippets, ...).
        // TODO make this automatic.
        if (this.parallaxEl) {
            this._refreshPublicWidgets();
        }
    },
    /**
     * @override
     */
    onMove() {
        this._refreshPublicWidgets();
    },
    /**
     * @override
     */
    destroy() {
        this._super(...arguments);
        this.$target.off('.ParallaxOption');
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * Build/remove parallax.
     *
     * @see this.selectClass for parameters
     */
    async selectDataAttribute(previewMode, widgetValue, params) {
        await this._super(...arguments);
        if (params.attributeName !== 'scrollBackgroundRatio') {
            return;
        }

        const isParallax = (widgetValue !== '0');
        this.$target.toggleClass('parallax', isParallax);
        this.$target.toggleClass('s_parallax_is_fixed', widgetValue === '1');
        this.$target.toggleClass('s_parallax_no_overflow_hidden', (widgetValue === '0' || widgetValue === '1'));
        if (isParallax) {
            if (!this.parallaxEl) {
                this.parallaxEl = document.createElement('span');
                this.parallaxEl.classList.add('s_parallax_bg');
                this.$target.prepend(this.parallaxEl);
            }
        } else {
            if (this.parallaxEl) {
                this.parallaxEl.remove();
                this.parallaxEl = null;
            }
        }

        this._updateBackgroundOptions();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _computeVisibility(widgetName) {
        return !this.$target.hasClass('o_background_video');
    },
    /**
     * @override
     */
    async _computeWidgetState(methodName, params) {
        if (methodName === 'selectDataAttribute' && params.parallaxTypeOpt) {
            const attrName = params.attributeName;
            const attrValue = (this.$target[0].dataset[attrName] || params.attributeDefaultValue).trim();
            switch (attrValue) {
                case '0':
                case '1': {
                    return attrValue;
                }
                default: {
                    return (attrValue.startsWith('-') ? '-1.5' : '1.5');
                }
            }
        }
        return this._super(...arguments);
    },
    /**
     * Updates external background-related option to work with the parallax
     * element instead of the original target when necessary.
     *
     * @private
     */
    _updateBackgroundOptions() {
        this.trigger_up('option_update', {
            optionNames: ['BackgroundImage', 'BackgroundPosition', 'BackgroundOptimize'],
            name: 'target',
            data: this.parallaxEl ? $(this.parallaxEl) : this.$target,
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called on any snippet update to check if the parallax should still be
     * enabled or not.
     *
     * TODO there is probably a better system to implement to solve this issue.
     *
     * @private
     * @param {Event} ev
     */
    _onExternalUpdate(ev) {
        if (!this.parallaxEl) {
            return;
        }
        const bgImage = this.parallaxEl.style.backgroundImage;
        if (!bgImage || bgImage === 'none' || this.$target.hasClass('o_background_video')) {
            // The parallax option was enabled but the background image was
            // removed: disable the parallax option.
            const widget = this._requestUserValueWidgets('parallax_none_opt')[0];
            widget.enable();
            widget.getParent().close(); // FIXME remove this ugly hack asap
        }
    },
});

options.registry.collapse = options.Class.extend({
    /**
     * @override
     */
    start: function () {
        var self = this;
        this.$bsTarget.on('shown.bs.collapse hidden.bs.collapse', '[role="tabpanel"]', function () {
            self.trigger_up('cover_update');
            self.$target.trigger('content_changed');
        });
        return this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    onBuilt: function () {
        this._createIDs();
    },
    /**
     * @override
     */
    onClone: function () {
        this._createIDs();
    },
    /**
     * @override
     */
    onMove: function () {
        this._createIDs();
        var $panel = this.$bsTarget.find('.collapse').removeData('bs.collapse');
        if ($panel.attr('aria-expanded') === 'true') {
            $panel.closest('.accordion').find('.collapse[aria-expanded="true"]')
                .filter((i, el) => (el !== $panel[0]))
                .collapse('hide')
                .one('hidden.bs.collapse', function () {
                    $panel.trigger('shown.bs.collapse');
                });
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Associates unique ids on collapse elements.
     *
     * @private
     */
    _createIDs: function () {
        let time = new Date().getTime();
        const $tablist = this.$target.closest('[role="tablist"]');
        const $tab = this.$target.find('[role="tab"]');
        const $panel = this.$target.find('[role="tabpanel"]');
<<<<<<< HEAD
        const $body = this.$target.closest('body');

        const setUniqueId = ($elem, label) => {
            let elemId = $elem.attr('id');
            if (!elemId || $body.find('[id="' + elemId + '"]').length > 1) {
                do {
                    time++;
                    elemId = label + time;
                } while ($body.find('#' + elemId).length);
=======

        const setUniqueId = ($elem, label) => {
            let elemId = $elem.attr('id');
            if (!elemId || $('[id="' + elemId + '"]').length > 1) {
                do {
                    time++;
                    elemId = label + time;
                } while ($('#' + elemId).length);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                $elem.attr('id', elemId);
            }
            return elemId;
        };

        const tablistId = setUniqueId($tablist, 'myCollapse');
<<<<<<< HEAD
        $panel.attr('data-bs-parent', '#' + tablistId);
        $panel.data('bs-parent', '#' + tablistId);

        const panelId = setUniqueId($panel, 'myCollapseTab');
        $tab.attr('data-bs-target', '#' + panelId);
        $tab.data('bs-target', '#' + panelId);
    },
});

options.registry.WebsiteLevelColor = options.Class.extend({
    specialCheckAndReloadMethodsNames: options.Class.prototype.specialCheckAndReloadMethodsNames
        .concat(['customizeWebsiteLayer2Color']),

    /**
     * @see this.selectClass for parameters
     */
    async customizeWebsiteLayer2Color(previewMode, widgetValue, params) {
        if (previewMode) {
            return;
        }
        params.color = params.layerColor;
        params.variable = params.layerGradient;
        let color = undefined;
        let gradient = undefined;
        if (weUtils.isColorGradient(widgetValue)) {
            color = '';
            gradient = widgetValue;
        } else {
            color = widgetValue;
            gradient = '';
        }
        await this.customizeWebsiteVariable(previewMode, gradient, params);
        params.noBundleReload = false;
        return this.customizeWebsiteColor(previewMode, color, params);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _computeWidgetState(methodName, params) {
        if (methodName === 'customizeWebsiteLayer2Color') {
            params.variable = params.layerGradient;
            const gradient = await this._computeWidgetState('customizeWebsiteVariable', params);
            if (gradient) {
                return gradient.substring(1, gradient.length - 1); // Unquote
            }
            params.color = params.layerColor;
            return this._computeWidgetState('customizeWebsiteColor', params);
        }
        return this._super(...arguments);
    },
});

options.registry.HeaderLayout = options.registry.WebsiteLevelColor.extend({
    /**
     * @overide
     */
    async customizeWebsiteViews(previewMode, widgetValue, params) {
        const _super = this._super.bind(this);

        if (params.name === 'header_sidebar_opt') {
            // When the user selects sidebar as header, make sure that the
            // header position is regular.
            await new Promise(resolve => {
                this.trigger_up('action_demand', {
                    actionName: 'toggle_page_option',
                    params: [{name: 'header_overlay', value: false}],
                    onSuccess: () => resolve(),
                });
            });
        }

        return _super(...arguments);
    }
});

=======
        $panel.attr('data-parent', '#' + tablistId);
        $panel.data('parent', '#' + tablistId);

        const panelId = setUniqueId($panel, 'myCollapseTab');
        $tab.attr('data-target', '#' + panelId);
        $tab.data('target', '#' + panelId);
    },
});

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
options.registry.HeaderNavbar = options.Class.extend({
    /**
     * Particular case: we want the option to be associated on the header navbar
     * in XML so that the related options only appear on navbar click (not
     * header), in a different section, etc... but we still want the target to
     * be the header itself.
     *
     * @constructor
     */
    init() {
        this._super(...arguments);
<<<<<<< HEAD
        this.setTarget(this.$target.closest('#wrapwrap > header'));
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async updateUIVisibility() {
        await this._super(...arguments);

        // TODO improve this: this is a big hack so that the "no mobile
        // hamburger" option is disabled if it is ever hidden (because of the
        // selection of an hamburger template which is a foreign option). This
        // should be done another way in another place somehow...
        const noHamburgerWidget = this.findWidget('no_hamburger_opt');
        const noHamburgerHidden = noHamburgerWidget.$el.hasClass('d-none');
        if (noHamburgerHidden && noHamburgerWidget.isActive()) {
            this.findWidget('default_hamburger_opt').enable();
        }

        // TODO improve this: this is a big hack so that the label of the
        // hamburger option changes if the 'no_hamburger_opt' one is available
        // (= in that case the option controls only the *mobile* hamburger).
        const hamburgerTypeWidget = this.findWidget('header_hamburger_type_opt');
        const labelEl = hamburgerTypeWidget.el.querySelector('we-title');
        if (!this._originalHamburgerTypeLabel) {
            this._originalHamburgerTypeLabel = labelEl.textContent;
        }
        labelEl.textContent = noHamburgerHidden
            ? this._originalHamburgerTypeLabel
            : _t("Mobile menu");
=======
        // Don't use setTarget, we want it to be set directly at initialization.
        this.$target = this.$target.closest('#wrapwrap > header');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async start() {
        await this._super(...arguments);
        // TODO Remove in master.
        const signInOptionEl = this.el.querySelector('[data-customize-website-views="portal.user_sign_in"]');
        signInOptionEl.dataset.noPreview = 'true';
    },
    /**
     * @private
     */
    async updateUI() {
        await this._super(...arguments);
        // For all header templates except those in the following array, change
        // the label of the option to "Mobile Alignment" (instead of
        // "Alignment") because it only impacts the mobile view.
<<<<<<< HEAD
        if (!["'default'", "'hamburger'", "'sidebar'", "'magazine'", "'hamburger-full'", "'slogan'"]
=======
        if (!["'default'", "'hamburger'", "'sidebar'", "'magazine'", "'hamburger-full'"]
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            .includes(weUtils.getCSSVariableValue("header-template"))) {
            const alignmentOptionTitleEl = this.el.querySelector('[data-name="header_alignment_opt"] we-title');
            alignmentOptionTitleEl.textContent = _t("Mobile Alignment");
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Needs to be done manually for now because data-dependencies
     * doesn't work with "AND" conditions.
     * TODO: improve this.
     *
     * @override
     */
    async _computeWidgetVisibility(widgetName, params) {
<<<<<<< HEAD
        switch (widgetName) {
            case 'option_logo_height_scrolled': {
                return !!this.$('.navbar-brand').length;
            }
            case 'no_hamburger_opt': {
                return !weUtils.getCSSVariableValue('header-template').includes('hamburger');
            }
        }
        if (widgetName === 'header_alignment_opt') {
            if (!this.$target[0].querySelector('.o_offcanvas_menu_toggler')) {
                // If mobile menu is "Default", hides the alignment option for
                // "hamburger full" and "magazine" header templates.
                return !["'hamburger-full'", "'magazine'"].includes(weUtils.getCSSVariableValue('header-template'));
=======
        if (widgetName === 'option_logo_height_scrolled') {
            return !!this.$('.navbar-brand').length;
        }
        if (widgetName === 'header_alignment_opt') {
            if (!this.$target[0].querySelector('.o_offcanvas_menu_toggler')) {
                // If hamburger type is "Default", hides the alignment option
                // for "hamburger full" and "magazine" header templates.
                return !this.$target[0].querySelector('#oe_structure_header_hamburger_full_1, #oe_structure_header_magazine_1');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
            return true;
        }
        return this._super(...arguments);
    },
});

const VisibilityPageOptionUpdate = options.Class.extend({
    pageOptionName: undefined,
    showOptionWidgetName: undefined,
    shownValue: '',

    /**
     * @override
     */
    async start() {
        await this._super(...arguments);
<<<<<<< HEAD
=======
        // When entering edit mode via the URL (enable_editor) the WebsiteNavbar
        // is not yet ReadyForActions because it is waiting for its
        // sub-component EditPageMenu to start edit mode. Then invisible blocks
        // options start (so this option too). But for isShown() to work, the
        // navbar must be ReadyForActions. This is the reason why we can't wait
        // for isShown here, otherwise we would have a deadlock. On one hand the
        // navbar waiting for the invisible snippets options to be started to be
        // ReadyForActions and on the other hand this option which needs the
        // navbar to be ReadyForActions to be started.
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        // TODO in master: Use the data-invisible system to get rid of this
        // piece of code.
        this._isShown().then(isShown => {
            this.trigger_up('snippet_option_visibility_update', {show: isShown});
        });
    },
    /**
     * @override
     */
    async onTargetShow() {
        if (await this._isShown()) {
            // onTargetShow may be called even if the element is already shown.
            // In most cases, this is not a problem but here it is as the code
            // that follows clicks on the visibility checkbox regardless of its
            // status. This avoids searching for that checkbox entirely.
            return;
        }
        // TODO improve: here we make a hack so that if we make the invisible
        // header appear for edition, its actual visibility for the page is
        // toggled (otherwise it would be about editing an element which
        // is actually never displayed on the page).
        const widget = this._requestUserValueWidgets(this.showOptionWidgetName)[0];
        widget.enable();
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @see this.selectClass for params
     */
    async visibility(previewMode, widgetValue, params) {
        const show = (widgetValue !== 'hidden');
        await new Promise((resolve, reject) => {
            this.trigger_up('action_demand', {
                actionName: 'toggle_page_option',
                params: [{name: this.pageOptionName, value: show}],
                onSuccess: () => resolve(),
                onFailure: reject,
            });
        });
        this.trigger_up('snippet_option_visibility_update', {show: show});
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _computeWidgetState(methodName, params) {
        if (methodName === 'visibility') {
            const shown = await this._isShown();
            return shown ? this.shownValue : 'hidden';
        }
        return this._super(...arguments);
    },
    /**
     * @private
     * @returns {boolean}
     */
    async _isShown() {
        return new Promise((resolve, reject) => {
            this.trigger_up('action_demand', {
                actionName: 'get_page_option',
                params: [this.pageOptionName],
                onSuccess: v => resolve(!!v),
                onFailure: reject,
            });
        });
    },
});

options.registry.TopMenuVisibility = VisibilityPageOptionUpdate.extend({
    pageOptionName: 'header_visible',
    showOptionWidgetName: 'regular_header_visibility_opt',

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * Handles the switching between 3 differents visibilities of the header.
     *
     * @see this.selectClass for params
     */
    async visibility(previewMode, widgetValue, params) {
        await this._super(...arguments);
        await this._changeVisibility(widgetValue);
        // TODO this is hacky but changing the header visibility may have an
        // effect on features like FullScreenHeight which depend on viewport
        // size so we simulate a resize.
<<<<<<< HEAD
        const targetWindow = this.$target[0].ownerDocument.defaultView;
        targetWindow.dispatchEvent(new targetWindow.Event('resize'));
=======
        $(window).trigger('resize');
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _changeVisibility(widgetValue) {
        const show = (widgetValue !== 'hidden');
        if (!show) {
            return;
        }
        const transparent = (widgetValue === 'transparent');
        await new Promise(resolve => {
            this.trigger_up('action_demand', {
                actionName: 'toggle_page_option',
                params: [{name: 'header_overlay', value: transparent}],
                onSuccess: () => resolve(),
            });
        });
        if (!transparent) {
            return;
        }
        await new Promise(resolve => {
            this.trigger_up('action_demand', {
                actionName: 'toggle_page_option',
                params: [{name: 'header_color', value: ''}],
                onSuccess: () => resolve(),
            });
        });
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    /**
     * @override
     */
    async _changeVisibility(widgetValue) {
        const show = (widgetValue !== 'hidden');
        if (!show) {
            return;
        }
        const transparent = (widgetValue === 'transparent');
        await new Promise((resolve, reject) => {
            this.trigger_up('action_demand', {
                actionName: 'toggle_page_option',
                params: [{name: 'header_overlay', value: transparent}],
                onSuccess: () => resolve(),
                onFailure: reject,
            });
        });
        if (!transparent) {
            return;
        }
        await new Promise((resolve, reject) => {
            this.trigger_up('action_demand', {
                actionName: 'toggle_page_option',
                params: [{name: 'header_color', value: ''}],
                onSuccess: () => resolve(),
                onFailure: reject,
            });
        });
    },
    /**
     * @override
     */
    async _computeWidgetState(methodName, params) {
        const _super = this._super.bind(this);
        if (methodName === 'visibility') {
            this.shownValue = await new Promise((resolve, reject) => {
                this.trigger_up('action_demand', {
                    actionName: 'get_page_option',
                    params: ['header_overlay'],
                    onSuccess: v => resolve(v ? 'transparent' : 'regular'),
                    onFailure: reject,
                });
            });
        }
        return _super(...arguments);
    },
    /**
     * @override
     */
    _computeWidgetVisibility(widgetName, params) {
        if (widgetName === 'header_visibility_opt') {
            return this.$target[0].classList.contains('o_header_sidebar') ? '' : 'true';
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    _renderCustomXML(uiFragment) {
        // TODO in master: put this in the XML.
        const weSelectEl = uiFragment.querySelector('we-select#option_header_visibility');
        if (weSelectEl) {
            weSelectEl.dataset.name = 'header_visibility_opt';
        }
    },
});

options.registry.topMenuColor = options.Class.extend({

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async selectStyle(previewMode, widgetValue, params) {
        await this._super(...arguments);
        const className = widgetValue ? (params.colorPrefix + widgetValue) : '';
        await new Promise((resolve, reject) => {
            this.trigger_up('action_demand', {
                actionName: 'toggle_page_option',
                params: [{name: 'header_color', value: className}],
                onSuccess: resolve,
                onFailure: reject,
            });
        });
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeVisibility: async function () {
        const show = await this._super(...arguments);
        if (!show) {
            return false;
        }
        return new Promise((resolve, reject) => {
            this.trigger_up('action_demand', {
                actionName: 'get_page_option',
                params: ['header_overlay'],
                onSuccess: value => resolve(!!value),
                onFailure: reject,
            });
        });
    },
});

/**
<<<<<<< HEAD
 * Manage the visibility of snippets on mobile/desktop.
 */
options.registry.DeviceVisibility = options.Class.extend({
=======
 * Manage the visibility of snippets on mobile.
 */
options.registry.MobileVisibility = options.Class.extend({
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
<<<<<<< HEAD
     * Toggles the device visibility.
     *
     * @see this.selectClass for parameters
     */
    async toggleDeviceVisibility(previewMode, widgetValue, params) {
        this.$target[0].classList.remove('d-none', 'd-md-none', 'd-lg-none',
            'o_snippet_mobile_invisible', 'o_snippet_desktop_invisible',
            'o_snippet_override_invisible',
        );
        const style = getComputedStyle(this.$target[0]);
        this.$target[0].classList.remove(`d-md-${style['display']}`, `d-lg-${style['display']}`);
        if (widgetValue === 'no_desktop') {
            this.$target[0].classList.add('d-lg-none', 'o_snippet_desktop_invisible');
        } else if (widgetValue === 'no_mobile') {
            this.$target[0].classList.add(`d-lg-${style['display']}`, 'd-none', 'o_snippet_mobile_invisible');
        }

        // Update invisible elements.
        let isMobile;
        this.trigger_up('service_context_get', {
            callback: (ctx) => {
                isMobile = ctx['isMobile'];
            },
        });
        this.trigger_up('snippet_option_visibility_update', {show: widgetValue !== (isMobile ? 'no_mobile' : 'no_desktop')});
    },
    /**
     * @override
     */
    async onTargetHide() {
        this.$target[0].classList.remove('o_snippet_override_invisible');
    },
    /**
     * @override
     */
    async onTargetShow() {
        if (this.$target[0].classList.contains('o_snippet_mobile_invisible')
                || this.$target[0].classList.contains('o_snippet_desktop_invisible')) {
            this.$target[0].classList.add('o_snippet_override_invisible');
        }
    },
    /**
     * @override
     */
    cleanForSave() {
        this.$target[0].classList.remove('o_snippet_override_invisible');
=======
     * Allows to show or hide the associated snippet in mobile display mode.
     *
     * @see this.selectClass for parameters
     */
    showOnMobile(previewMode, widgetValue, params) {
        // For compatibility with former implementation: remove the previously
        // added `d-md-*` class if any, as it should now be `d-lg-*`.
        if (widgetValue) {
            this.$target[0].classList.remove(`d-md-${this.$target.css('display')}`);
        }
        const classes = `d-none d-lg-${this.$target.css('display')}`;
        this.$target.toggleClass(classes, !widgetValue);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _computeWidgetState(methodName, params) {
<<<<<<< HEAD
        if (methodName === 'toggleDeviceVisibility') {
            const classList = [...this.$target[0].classList];
            if (classList.includes('d-none') &&
                    classList.some(className => className.match(/^d-(md|lg)-/))) {
                return 'no_mobile';
            }
            if (classList.some(className => className.match(/d-(md|lg)-none/))) {
                return 'no_desktop';
            }
            return '';
        }
        return await this._super(...arguments);
    },
    /**
     * @override
     */
    _computeWidgetVisibility(widgetName, params) {
        if (this.$target[0].classList.contains('s_table_of_content_main')) {
            return false;
        }
        return this._super(...arguments);
    }
=======
        if (methodName === 'showOnMobile') {
            const classList = [...this.$target[0].classList];
            return classList.includes('d-none') &&
                classList.some(className => className.match(/^(d-md-|d-lg-)/g)) ? '' : 'true';
        }
        return await this._super(...arguments);
    },
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
});

/**
 * Hide/show footer in the current page.
 */
options.registry.HideFooter = VisibilityPageOptionUpdate.extend({
    pageOptionName: 'footer_visible',
    showOptionWidgetName: 'hide_footer_page_opt',
    shownValue: 'shown',
});

/**
 * Handles the edition of snippet's anchor name.
 */
options.registry.anchor = options.Class.extend({
    isTopOption: true,

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    start: function () {
        // Generate anchor and copy it to clipboard on click, show the tooltip on success
        this.$button = this.$el.find('we-button');
        const clipboard = new ClipboardJS(this.$button[0], {text: () => this._getAnchorLink()});
        clipboard.on('success', () => {
<<<<<<< HEAD
            const message = sprintf(Markup(_t("Anchor copied to clipboard<br>Link: %s")), this._getAnchorLink());
            this.displayNotification({
              type: 'success',
              message: message,
=======
            this.displayNotification({
              type: 'success',
              message: _.str.sprintf(_t("Anchor copied to clipboard<br>Link: %s"), this._getAnchorLink()),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
              buttons: [{text: _t("Edit"), click: () => this.openAnchorDialog(), primary: true}],
            });
        });

        return this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    onClone: function () {
        this.$target.removeAttr('data-anchor');
        this.$target.filter(':not(.carousel)').removeAttr('id');
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * @see this.selectClass for parameters
     */
    openAnchorDialog: function (previewMode, widgetValue, params) {
        var self = this;
        var buttons = [{
            text: _t("Save & copy"),
            classes: 'btn-primary',
            click: function () {
                var $input = this.$('.o_input_anchor_name');
                var anchorName = self._text2Anchor($input.val());
                if (self.$target[0].id === anchorName) {
                    // If the chosen anchor name is already the one used by the
                    // element, close the dialog and do nothing else
                    this.close();
                    return;
                }

                const alreadyExists = !!document.getElementById(anchorName);
                this.$('.o_anchor_already_exists').toggleClass('d-none', !alreadyExists);
                $input.toggleClass('is-invalid', alreadyExists);
                if (!alreadyExists) {
                    self._setAnchorName(anchorName);
                    this.close();
                    self.$button[0].click();
                }
            },
        }, {
            text: _t("Discard"),
            close: true,
        }];
        if (this.$target.attr('id')) {
            buttons.push({
                text: _t("Remove"),
                classes: 'btn-link ms-auto',
                icon: 'fa-trash',
                close: true,
                click: function () {
                    self._setAnchorName();
                },
            });
        }
        new Dialog(this, {
            title: _t("Link Anchor"),
            $content: $(qweb.render('website.dialog.anchorName', {
                currentAnchor: decodeURIComponent(this.$target.attr('id')),
            })),
            buttons: buttons,
        }).open();
    },
    /**
     * @private
     * @param {String} value
     */
    _setAnchorName: function (value) {
        if (value) {
            this.$target.attr({
                'id': value,
                'data-anchor': true,
            });
        } else {
            this.$target.removeAttr('id data-anchor');
        }
        this.$target.trigger('content_changed');
    },
    /**
     * Returns anchor text.
     *
     * @private
     * @returns {string}
     */
    _getAnchorLink: function () {
        if (!this.$target[0].id) {
            const $titles = this.$target.find('h1, h2, h3, h4, h5, h6');
            const title = $titles.length > 0 ? $titles[0].innerText : this.data.snippetName;
            const anchorName = this._text2Anchor(title);
            let n = '';
            while (document.getElementById(anchorName + n)) {
                n = (n || 1) + 1;
            }
            this._setAnchorName(anchorName + n);
        }
        return `${this.ownerDocument.location.pathname}#${this.$target[0].id}`;
    },
    /**
     * Creates a safe id/anchor from text.
     *
     * @private
     * @param {string} text
     * @returns {string}
     */
    _text2Anchor: function (text) {
        return encodeURIComponent(text.trim().replace(/\s+/g, '-'));
    },
});

options.registry.HeaderBox = options.registry.Box.extend({

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
<<<<<<< HEAD
     * @override
     */
    async selectStyle(previewMode, widgetValue, params) {
        if ((params.variable || params.color)
                && ['border-width', 'border-style', 'border-color', 'border-radius', 'box-shadow'].includes(params.cssProperty)) {
            if (previewMode) {
                return;
=======
     * TODO this should be reviewed in master to avoid the need of using the
     * 'reset' previewMode and having to remember the previous box-shadow value.
     * We are forced to remember the previous box shadow before applying a new
     * one as the whole box-shadow value is handled by multiple widgets.
     *
     * @see this.selectClass for parameters
     */
    async setShadow(previewMode, widgetValue, params) {
        // Check if the currently configured shadow is not using the same shadow
        // mode, in which case nothing has to be done.
        const styles = window.getComputedStyle(this.$target[0]);
        const currentBoxShadow = styles['box-shadow'] || 'none';
        const currentMode = currentBoxShadow === 'none'
            ? ''
            : currentBoxShadow.includes('inset') ? 'inset' : 'outset';
        if (currentMode === widgetValue) {
            return;
        }

        if (previewMode === true) {
            this._prevBoxShadow = currentBoxShadow;
        }

        // Add/remove the shadow class
        this.$target.toggleClass(params.shadowClass, !!widgetValue);

        // Change the mode of the old box shadow. If no shadow was currently
        // set then get the shadow value that is supposed to be set according
        // to the shadow mode. Try to apply it via the selectStyle method so
        // that it is either ignored because the shadow class had its effect or
        // forced (to the shadow value or none) if toggling the class is not
        // enough (e.g. if the item has a default shadow coming from CSS rules,
        // removing the shadow class won't be enough to remove the shadow but in
        // most other cases it will).
        let shadow = 'none';
        if (previewMode === 'reset') {
            shadow = this._prevBoxShadow;
        } else {
            if (currentBoxShadow === 'none') {
                shadow = this._getDefaultShadow(widgetValue, params.shadowClass) || 'none';
            } else {
                if (widgetValue === 'outset') {
                    shadow = currentBoxShadow.replace('inset', '').trim();
                } else if (widgetValue === 'inset') {
                    shadow = currentBoxShadow + ' inset';
                }
            }
        }
        await this.selectStyle(previewMode, shadow, Object.assign({cssProperty: 'box-shadow'}, params));
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeWidgetState(methodName, params) {
        if (methodName === 'setShadow') {
            const shadowValue = this.$target.css('box-shadow');
            if (!shadowValue || shadowValue === 'none') {
                return '';
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
            if (params.cssProperty === 'border-color') {
                return this.customizeWebsiteColor(previewMode, widgetValue, params);
            }
            return this.customizeWebsiteVariable(previewMode, widgetValue, params);
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    async setShadow(previewMode, widgetValue, params) {
        if (params.variable) {
            if (previewMode) {
                return;
            }
            const defaultShadow = this._getDefaultShadow(widgetValue, params.shadowClass);
            return this.customizeWebsiteVariable(previewMode, defaultShadow, params);
        }
        return this._super(...arguments);
    },
    /**
     * @private
     * @param {string} type
     * @param {string} shadowClass
     * @returns {string}
     */
    _getDefaultShadow(type, shadowClass) {
        const el = document.createElement('div');
        if (type) {
            el.classList.add(shadowClass);
        }

        let shadow = ''; // TODO in master this should be changed to 'none'
        document.body.appendChild(el);
        switch (type) {
            case 'outset': {
                shadow = $(el).css('box-shadow');
                break;
            }
            case 'inset': {
                shadow = $(el).css('box-shadow') + ' inset';
                break;
            }
        }
        el.remove();
        return shadow;
    }
});

options.registry.HeaderBox = options.registry.Box.extend({

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async selectStyle(previewMode, widgetValue, params) {
        if ((params.variable || params.color)
                && ['border-width', 'border-style', 'border-color', 'border-radius', 'box-shadow'].includes(params.cssProperty)) {
            if (previewMode) {
                return;
            }
            if (params.cssProperty === 'border-color') {
                return this.customizeWebsiteColor(previewMode, widgetValue, params);
            }
            return this.customizeWebsiteVariable(previewMode, widgetValue, params);
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    async setShadow(previewMode, widgetValue, params) {
        if (params.variable) {
            if (previewMode) {
                return;
            }
            const defaultShadow = this._getDefaultShadow(widgetValue, params.shadowClass);
            return this.customizeWebsiteVariable(previewMode, defaultShadow || 'none', params);
        }
        return this._super(...arguments);
    },
});

options.registry.CookiesBar = options.registry.SnippetPopup.extend({
    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * Change the cookies bar layout.
     *
     * @see this.selectClass for parameters
     */
    selectLayout: function (previewMode, widgetValue, params) {
        let websiteId;
        this.trigger_up('context_get', {
            callback: function (ctx) {
                websiteId = ctx['website_id'];
            },
        });

        const $template = $(qweb.render(`website.cookies_bar.${widgetValue}`, {
            websiteId: websiteId,
        }));

        const $content = this.$target.find('.modal-content');
        
        // The order of selectors is significant since certain selectors may be 
        // nested within others, and we want to preserve the nested ones.
        // For instance, in the case of '.o_cookies_bar_text_policy' nested
        // inside '.o_cookies_bar_text_secondary', the parent selector should be
        // copied first, followed by the child selector to ensure that the
        // content of the nested selector is not overwritten.
        const selectorsToKeep = [
            '.o_cookies_bar_text_button',
            '.o_cookies_bar_text_button_essential',
            '.o_cookies_bar_text_title',
            '.o_cookies_bar_text_primary',
            '.o_cookies_bar_text_secondary',
            '.o_cookies_bar_text_policy'
        ];

        if (this.$savedSelectors === undefined) {
            this.$savedSelectors = [];
        }

        for (const selector of selectorsToKeep) {
            const $currentLayoutEls = $content.find(selector).contents();
            const $newLayoutEl = $template.find(selector);
            if ($currentLayoutEls.length) {
                // save value before change, eg 'title' is not inside 'discrete' template
                // but we want to preserve it in case of select another layout later
                this.$savedSelectors[selector] = $currentLayoutEls;
            }
            const $savedSelector = this.$savedSelectors[selector];
            if ($newLayoutEl.length && $savedSelector && $savedSelector.length) {
                $newLayoutEl.empty().append($savedSelector);
            }
        }

        $content.empty().append($template);
    },
});

/**
 * Allows edition of 'cover_properties' in website models which have such
 * fields (blogs, posts, events, ...).
 */
options.registry.CoverProperties = options.Class.extend({
    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);

        this.$image = this.$target.find('.o_record_cover_image');
        this.$filter = this.$target.find('.o_record_cover_filter');
    },
    /**
     * @override
     */
    start: function () {
        this.$filterValueOpts = this.$el.find('[data-filter-value]');

        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * Handles a background change.
     *
     * @see this.selectClass for parameters
     */
    background: async function (previewMode, widgetValue, params) {
        if (widgetValue === '') {
            this.$image.css('background-image', '');
            this.$target.removeClass('o_record_has_cover');
        } else {
            this.$image.css('background-image', `url('${widgetValue}')`);
            this.$target.addClass('o_record_has_cover');
            const $defaultSizeBtn = this.$el.find('.o_record_cover_opt_size_default');
            $defaultSizeBtn.click();
            $defaultSizeBtn.closest('we-select').click();
        }

        if (!previewMode) {
            this._updateSavingDataset();
        }
    },
    /**
     * @see this.selectClass for parameters
     */
    filterValue: function (previewMode, widgetValue, params) {
        this.$filter.css('opacity', widgetValue || 0);
        this.$filter.toggleClass('oe_black', parseFloat(widgetValue) !== 0);

        if (!previewMode) {
            this._updateSavingDataset();
        }
    },
    /**
     * @override
     */
    selectStyle: async function (previewMode, widgetValue, params) {
        await this._super(...arguments);

<<<<<<< HEAD
        if (!previewMode) {
            this._updateSavingDataset(widgetValue);
        }
    },
    /**
     * @override
     */
    selectClass: async function (previewMode, widgetValue, params) {
        await this._super(...arguments);

        if (!previewMode) {
            this._updateSavingDataset();
        }
=======
        // TODO: `o_record_has_cover` should be handled using model field, not
        // resize_class to avoid all of this.
        let coverClass = this.$el.find('[data-cover-opt-name="size"] we-button.active').data('selectClass') || '';
        const bg = this.$image.css('background-image');
        if (bg && bg !== 'none') {
            coverClass += " o_record_has_cover";
        }
        // Update saving dataset
        this.$target[0].dataset.coverClass = coverClass;
        this.$target[0].dataset.textAlignClass = this.$el.find('[data-cover-opt-name="text_align"] we-button.active').data('selectClass') || '';
        this.$target[0].dataset.filterValue = this.$filterValueOpts.filter('.active').data('filterValue') || 0.0;
        let colorPickerWidget = null;
        this.trigger_up('user_value_widget_request', {
            name: 'bg_color_opt',
            onSuccess: _widget => colorPickerWidget = _widget,
        });
        const color = colorPickerWidget._value;
        const isCSSColor = ColorpickerWidget.isCSSColor(color);
        this.$target[0].dataset.bgColorClass = isCSSColor ? '' : weUtils.computeColorClasses([color])[0];
        this.$target[0].dataset.bgColorStyle = isCSSColor ? `background-color: ${color};` : '';
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeWidgetState: function (methodName, params) {
        switch (methodName) {
            case 'filterValue': {
                return parseFloat(this.$filter.css('opacity')).toFixed(1);
            }
            case 'background': {
                const background = this.$image.css('background-image');
                if (background && background !== 'none') {
                    return background.match(/^url\(["']?(.+?)["']?\)$/)[1];
                }
                return '';
            }
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    _computeWidgetVisibility: function (widgetName, params) {
        if (params.coverOptName) {
            return this.$target.data(`use_${params.coverOptName}`) === 'True';
        }
        return this._super(...arguments);
    },
    /**
     * @private
     */
    _updateColorDataset(bgColorStyle = '', bgColorClass = '') {
        this.$target[0].dataset.bgColorStyle = bgColorStyle;
        this.$target[0].dataset.bgColorClass = bgColorClass;
    },
    /**
     * Updates the cover properties dataset used for saving.
     *
     * @private
     */
    _updateSavingDataset(colorValue) {
        const [colorPickerWidget, sizeWidget, textAlignWidget] = this._requestUserValueWidgets('bg_color_opt', 'size_opt', 'text_align_opt');
        // TODO: `o_record_has_cover` should be handled using model field, not
        // resize_class to avoid all of this.
        // Get values from DOM (selected values in options are only available
        // after updateUI)
        const sizeOptValues = sizeWidget.getMethodsParams('selectClass').possibleValues;
        let coverClass = [...this.$target[0].classList].filter(
            value => sizeOptValues.includes(value)
        ).join(' ');
        const bg = this.$image.css('background-image');
        if (bg && bg !== 'none') {
            coverClass += " o_record_has_cover";
        }
<<<<<<< HEAD
        const textAlignOptValues = textAlignWidget.getMethodsParams('selectClass').possibleValues;
        const textAlignClass = [...this.$target[0].classList].filter(
            value => textAlignOptValues.includes(value)
        ).join(' ');
        const filterEl = this.$target[0].querySelector('.o_record_cover_filter');
        const filterValue = filterEl && filterEl.style.opacity;
        // Update saving dataset
        this.$target[0].dataset.coverClass = coverClass;
        this.$target[0].dataset.textAlignClass = textAlignClass;
        this.$target[0].dataset.filterValue = filterValue || 0.0;
        // TODO there is probably a better way and this should be refactored to
        // use more standard colorpicker+imagepicker structure
        const ccValue = colorPickerWidget._ccValue;
        const colorOrGradient = colorPickerWidget._value;
        const isGradient = weUtils.isColorGradient(colorOrGradient);
        const isCSSColor = !isGradient && ColorpickerWidget.isCSSColor(colorOrGradient);
        const colorNames = [];
        if (ccValue) {
            colorNames.push(ccValue);
=======
        if (params.name === 'move_up_opt' || params.name === 'move_down_opt') {
            const mainScrollingEl = $().getScrollingElement()[0];
            const elTop = this.$target[0].getBoundingClientRect().top;
            const heightDiff = mainScrollingEl.offsetHeight - this.$target[0].offsetHeight;
            const bottomHidden = heightDiff < elTop;
            const hidden = elTop < 0 || bottomHidden;
            if (hidden) {
                dom.scrollTo(this.$target[0], {
                    extraOffset: 50,
                    forcedOffset: bottomHidden ? heightDiff - 50 : undefined,
                    easing: 'linear',
                    duration: 500,
                });
            }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        if (colorOrGradient && !isGradient && !isCSSColor) {
            colorNames.push(colorOrGradient);
        }
        const bgColorClass = weUtils.computeColorClasses(colorNames).join(' ');
        const bgColorStyle = isCSSColor ? `background-color: ${colorOrGradient};` :
            isGradient ? `background-color: rgba(0, 0, 0, 0); background-image: ${colorOrGradient};` : '';
        this._updateColorDataset(bgColorStyle, bgColorClass);
    },
});

options.registry.ScrollButton = options.Class.extend({
    /**
     * @override
     */
    start: async function () {
        await this._super(...arguments);
        this.$button = this.$('.o_scroll_button');
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @see this.selectClass for parameters
     */
    async showScrollButton(previewMode, widgetValue, params) {
        if (widgetValue) {
            this.$button.show();
        } else {
            if (previewMode) {
                this.$button.hide();
            } else {
                this.$button.detach();
            }
        }
    },
    /**
     * Toggles the scroll down button.
     */
    toggleButton: function (previewMode, widgetValue, params) {
        if (widgetValue) {
            if (!this.$button.length) {
                const anchor = document.createElement('a');
                anchor.classList.add(
                    'o_scroll_button',
                    'mb-3',
                    'rounded-circle',
                    'align-items-center',
                    'justify-content-center',
                    'mx-auto',
                    'bg-primary',
                    'o_not_editable',
                );
                anchor.href = '#';
                anchor.contentEditable = "false";
                anchor.title = _t("Scroll down to next section");
                const arrow = document.createElement('i');
                arrow.classList.add('fa', 'fa-angle-down', 'fa-3x');
                anchor.appendChild(arrow);
                this.$button = $(anchor);
            }
            this.$target.append(this.$button);
        } else {
            this.$button.detach();
        }
    },
    /**
     * @override
     */
    async selectClass(previewMode, widgetValue, params) {
        await this._super(...arguments);
        // If a "d-lg-block" class exists on the section (e.g., for mobile
        // visibility option), it should be replaced with a "d-lg-flex" class.
        // This ensures that the section has the "display: flex" property
        // applied, which is the default rule for both "height" option classes.
        if (params.possibleValues.includes("o_half_screen_height")) {
            if (widgetValue) {
                this.$target[0].classList.replace("d-lg-block", "d-lg-flex");
            } else if (this.$target[0].classList.contains("d-lg-flex")) {
                // There are no known cases, but we still make sure that the
                // <section> element doesn't have a "display: flex" originally.
                this.$target[0].classList.remove("d-lg-flex");
                const sectionStyle = window.getComputedStyle(this.$target[0]);
                const hasDisplayFlex = sectionStyle.getPropertyValue("display") === "flex";
                this.$target[0].classList.add(hasDisplayFlex ? "d-lg-flex" : "d-lg-block");
            }
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _renderCustomXML(uiFragment) {
        // TODO adapt in master. This sets up a different UI for the image
        // gallery snippet: for this one, we allow to force a specific height
        // in auto mode. It was done in stable as without it, the default height
        // is difficult to understand for the user as it depends on screen
        // height of the one who edited the website and not on the added images.
        // It was also a regression as in <= 11.0, this was a possibility.
        if (this.$target[0].dataset.snippet !== 's_image_gallery') {
            return;
        }
        let minHeightEl = uiFragment.querySelector('[data-name="minheight_auto_opt"]');
        if (!minHeightEl) {
            return;
        }
        minHeightEl = minHeightEl.parentElement;
        minHeightEl.setAttribute('string', _t("Min-Height"));
        const heightEl = document.createElement('we-input');
        heightEl.setAttribute('string', _t("Height"));
        heightEl.classList.add('o_we_sublevel_1');
        heightEl.dataset.dependencies = 'minheight_auto_opt';
        heightEl.dataset.unit = 'px';
        heightEl.dataset.selectStyle = '';
        heightEl.dataset.cssProperty = 'height';
        // For this setting, we need to always force the style (= if the block
        // is naturally 800px tall and the user enters 800px for this setting,
        // we set 800px as inline style anyway). Indeed, this snippet's style
        // is based on the height that is forced but once the related public
        // widgets are started, the inner carousel items receive a min-height
        // which makes it so the snippet "natural" height is equal to the
        // initially forced height... so if the style is not forced, it would
        // ultimately be removed by mistake thinking it is not necessary.
        // Note: this is forced as not important as we still need the height to
        // be reset to 'auto' in mobile (generic css rules).
        heightEl.dataset.forceStyle = '';
        uiFragment.appendChild(heightEl);
    },
    /**
     * @override
     */
    _computeWidgetState: function (methodName, params) {
        switch (methodName) {
            case 'toggleButton':
                return !!this.$button.parent().length;
        }
        return this._super(...arguments);
    },
});

<<<<<<< HEAD
options.registry.ConditionalVisibility = options.registry.DeviceVisibility.extend({
    /**
     * @constructor
     */
    init() {
        this._super(...arguments);
        this.optionsAttributes = [];
    },
    /**
     * @override
     */
    async start() {
        await this._super(...arguments);

        for (const widget of this._userValueWidgets) {
            const params = widget.getMethodsParams();
            if (params.saveAttribute) {
                this.optionsAttributes.push({
                    saveAttribute: params.saveAttribute,
                    attributeName: params.attributeName,
                    // If callWith dataAttribute is not specified, the default
                    // field to check on the record will be .value for values
                    // coming from another widget than M2M.
                    callWith: params.callWith || 'value',
                });
            }
        }
    },
    /**
     * @override
     */
    async onTargetHide() {
        await this._super(...arguments);
        if (this.$target[0].classList.contains('o_snippet_invisible')) {
            this.$target[0].classList.add('o_conditional_hidden');
        }
    },
    /**
     * @override
     */
    async onTargetShow() {
        await this._super(...arguments);
        this.$target[0].classList.remove('o_conditional_hidden');
    },
    // Todo: remove me in master.
    /**
     * @override
     */
    cleanForSave() {},

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * Inserts or deletes record's id and value in target's data-attributes
     * if no ids are selected, deletes the attribute.
     *
     * @see this.selectClass for parameters
     */
    selectRecord(previewMode, widgetValue, params) {
        const recordsData = JSON.parse(widgetValue);
        if (recordsData.length) {
            this.$target[0].dataset[params.saveAttribute] = widgetValue;
        } else {
            delete this.$target[0].dataset[params.saveAttribute];
        }

        this._updateCSSSelectors();
    },
    /**
     * Selects a value for target's data-attributes.
     * Should be used instead of selectRecord if the visibility is not related
     * to database values.
     *
     * @see this.selectClass for parameters
     */
    selectValue(previewMode, widgetValue, params) {
        if (widgetValue) {
            const widgetValueIndex = params.possibleValues.indexOf(widgetValue);
            const value = [{value: widgetValue, id: widgetValueIndex}];
            this.$target[0].dataset[params.saveAttribute] = JSON.stringify(value);
        } else {
            delete this.$target[0].dataset[params.saveAttribute];
        }

        this._updateCSSSelectors();
    },
    /**
     * Opens the toggler when 'conditional' is selected.
     *
     * @override
     */
    async selectDataAttribute(previewMode, widgetValue, params) {
        await this._super(...arguments);

        if (params.attributeName === 'visibility') {
            const targetEl = this.$target[0];
            if (widgetValue === 'conditional') {
                const collapseEl = this.$el.children('we-collapse')[0];
                this._toggleCollapseEl(collapseEl);
            } else {
                // TODO create a param to allow doing this automatically for genericSelectDataAttribute?
                delete targetEl.dataset.visibility;

                for (const attribute of this.optionsAttributes) {
                    delete targetEl.dataset[attribute.saveAttribute];
                    delete targetEl.dataset[`${attribute.saveAttribute}Rule`];
                }
            }
            this.trigger_up('snippet_option_visibility_update', {show: true});
        } else if (!params.isVisibilityCondition) {
            return;
        }

        this._updateCSSSelectors();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _computeWidgetState(methodName, params) {
        if (methodName === 'selectRecord') {
            return this.$target[0].dataset[params.saveAttribute] || '[]';
        }
        if (methodName === 'selectValue') {
            const selectedValue = this.$target[0].dataset[params.saveAttribute];
            return selectedValue ? JSON.parse(selectedValue)[0].value : params.attributeDefaultValue;
        }
        return this._super(...arguments);
    },
    /**
     * Reads target's attributes and creates CSS selectors.
     * Stores them in data-attributes to then be reapplied by
     * content/inject_dom.js (ideally we should saved them in a <style> tag
     * directly but that would require a new website.page field and would not
     * be possible in dynamic (controller) pages... maybe some day).
     *
     * @private
     */
    _updateCSSSelectors() {
        // There are 2 data attributes per option:
        // - One that stores the current records selected
        // - Another that stores the value of the rule "Hide for / Visible for"
        const visibilityIDParts = [];
        const onlyAttributes = [];
        const hideAttributes = [];
        const target = this.$target[0];
        for (const attribute of this.optionsAttributes) {
            if (target.dataset[attribute.saveAttribute]) {
                let records = JSON.parse(target.dataset[attribute.saveAttribute]).map(record => {
                    return { id: record.id, value: record[attribute.callWith] };
                });
                if (attribute.saveAttribute === 'visibilityValueLang') {
                    records = records.map(lang => {
                        lang.value = lang.value.replace(/_/g, '-');
                        return lang;
                    });
                }
                const hideFor = target.dataset[`${attribute.saveAttribute}Rule`] === 'hide';
                if (hideFor) {
                    hideAttributes.push({ name: attribute.attributeName, records: records});
                } else {
                    onlyAttributes.push({ name: attribute.attributeName, records: records});
                }
                // Create a visibilityId based on the options name and their
                // values. eg : hide for en_US(id:1) -> lang1h
                const type = attribute.attributeName.replace('data-', '');
                const valueIDs = records.map(record => record.id).sort();
                visibilityIDParts.push(`${type}_${hideFor ? 'h' : 'o'}_${valueIDs.join('_')}`);
            }
        }
        const visibilityId = visibilityIDParts.join('_');
        // Creates CSS selectors based on those attributes, the reducers
        // combine the attributes' values.
        let selectors = '';
        for (const attribute of onlyAttributes) {
            // e.g of selector:
            // html:not([data-attr-1="valueAttr1"]):not([data-attr-1="valueAttr2"]) [data-visibility-id="ruleId"]
            const selector = attribute.records.reduce((acc, record) => {
                return acc += `:not([${attribute.name}="${record.value}"])`;
            }, 'html') + ` body:not(.editor_enable) [data-visibility-id="${visibilityId}"]`;
            selectors += selector + ', ';
        }
        for (const attribute of hideAttributes) {
            // html[data-attr-1="valueAttr1"] [data-visibility-id="ruleId"],
            // html[data-attr-1="valueAttr2"] [data-visibility-id="ruleId"]
            const selector = attribute.records.reduce((acc, record, i, a) => {
                acc += `html[${attribute.name}="${record.value}"] body:not(.editor_enable) [data-visibility-id="${visibilityId}"]`;
                return acc + (i !== a.length - 1 ? ',' : '');
            }, '');
            selectors += selector + ', ';
        }
        selectors = selectors.slice(0, -2);
        if (selectors) {
            this.$target[0].dataset.visibilitySelectors = selectors;
        } else {
            delete this.$target[0].dataset.visibilitySelectors;
        }

        if (visibilityId) {
            this.$target[0].dataset.visibilityId = visibilityId;
        } else {
            delete this.$target[0].dataset.visibilityId;
        }
    },
});

options.registry.WebsiteAnimate = options.Class.extend({
    /**
     * @override
     */
    async start() {
        await this._super(...arguments);
        // Animations for which the "On Scroll" and "Direction" options are not
        // available.
        this.limitedAnimations = ['o_anim_flash', 'o_anim_pulse', 'o_anim_shake', 'o_anim_tada', 'o_anim_flip_in_x', 'o_anim_flip_in_y'];
        this.isAnimatedText = this.$target.hasClass('o_animated_text');
        this.$optionsSection = this.$overlay.data('$optionsSection');
        this.$scrollingElement = $().getScrollingElement(this.ownerDocument);
    },
    /**
     * @override
     */
    async onBuilt() {
        this.$target[0].classList.toggle('o_animate_preview', this.$target[0].classList.contains('o_animate'));
    },
    /**
     * @override
     */
    onFocus() {
        if (this.isAnimatedText) {
            // For animated text, the animation options must be in the editor
            // toolbar.
            const $toolbar = this.options.wysiwyg.toolbar.$el;
            $toolbar.append(this.$el);
            this.$optionsSection.addClass('d-none');
        }
    },
    /**
     * @override
     */
    onBlur() {
        if (this.isAnimatedText) {
            // For animated text, the options must be returned to their
            // original location as they were moved in the toolbar.
            this.$optionsSection.append(this.$el);
        }
    },
    /**
     * @override
     */
    cleanForSave() {
        if (this.$target[0].closest('.o_animate')) {
            // As images may have been added in an animated element, we must
            // remove the lazy loading on them.
            this._toggleImagesLazyLoading(false);
        }
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async selectClass(previewMode, widgetValue, params) {
        await this._super(...arguments);
        if (params.forceAnimation && params.name !== 'o_anim_no_effect_opt' && previewMode !== 'reset') {
            this._forceAnimation();
        }
        if (params.isAnimationTypeSelection) {
            this.$target[0].classList.toggle('o_animate_preview', !!widgetValue);
        }
    },
    /**
     * @override
     */
    async selectDataAttribute(previewMode, widgetValue, params) {
        await this._super(...arguments);
        if (params.forceAnimation) {
            this._forceAnimation();
        }
    },
    /**
     * Sets the animation mode.
     *
     * @see this.selectClass for parameters
     */
    animationMode(previewMode, widgetValue, params) {
        const targetClassList = this.$target[0].classList;
        this.$scrollingElement[0].classList.remove('o_wanim_overflow_xy_hidden');
        targetClassList.remove('o_animating', 'o_animate_both_scroll', 'o_visible', 'o_animated', 'o_animate_out');
        this.$target[0].style.animationDelay = '';
        this.$target[0].style.animationPlayState = '';
        this.$target[0].style.animationName = '';
        this.$target[0].style.visibility = '';
        if (widgetValue === 'onScroll') {
            this.$target[0].dataset.scrollZoneStart = 0;
            this.$target[0].dataset.scrollZoneEnd = 100;
        } else {
            delete this.$target[0].dataset.scrollZoneStart;
            delete this.$target[0].dataset.scrollZoneEnd;
        }
        if (!params.activeValue && widgetValue) {
            // If "Animation" was on "None" and it is no longer, it is set to
            // "fade_in" by default.
            targetClassList.add('o_anim_fade_in');
            this._toggleImagesLazyLoading(false);
        }
        if (!widgetValue) {
            const possibleEffects = this._requestUserValueWidgets('animation_effect_opt')[0].getMethodsParams('selectClass').possibleValues;
            const possibleDirections = this._requestUserValueWidgets('animation_direction_opt')[0].getMethodsParams('selectClass').possibleValues;
            const possibleEffectsAndDirections = possibleEffects.concat(possibleDirections);
            // Remove the classes added by "Effect" and "Direction" options if
            // "Animation" is "None".
            for (const targetClass of targetClassList.value.split(/\s+/g)) {
                if (possibleEffectsAndDirections.indexOf(targetClass) >= 0) {
                    targetClassList.remove(targetClass);
                }
            }
            this.$target[0].style.setProperty('--wanim-intensity', '');
            this.$target[0].style.animationDuration = '';
            this._toggleImagesLazyLoading(true);
        }
    },
    /**
     * Sets the animation intensity.
     *
     * @see this.selectClass for parameters
     */
    animationIntensity(previewMode, widgetValue, params) {
        this.$target[0].style.setProperty('--wanim-intensity', widgetValue);
        this._forceAnimation();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    async _forceAnimation() {
        this.$target.css('animation-name', 'dummy');

        if (this.$target[0].classList.contains('o_animate_on_scroll')) {
            // Trigger a DOM reflow.
            void this.$target[0].offsetWidth;
            this.$target.css('animation-name', '');
            this.ownerDocument.defaultView.dispatchEvent(new Event('resize'));
        } else {
            // Trigger a DOM reflow (Needed to prevent the animation from
            // being launched twice when previewing the "Intensity" option).
            await new Promise(resolve => setTimeout(resolve));
            this.$target.addClass('o_animating');
            this.trigger_up('cover_update', {
                overlayVisible: true,
            });
            this.$scrollingElement[0].classList.add('o_wanim_overflow_xy_hidden');
            this.$target.css('animation-name', '');
            this.$target.one('webkitAnimationEnd oanimationend msAnimationEnd animationend', () => {
                this.$scrollingElement[0].classList.remove('o_wanim_overflow_xy_hidden');
                this.$target.removeClass('o_animating');
            });
        }
=======
// TODO there is no data-js associated to this but a data-option-name, somehow
// it acts as data-js... it will be reviewed in master.
options.registry.minHeight = options.Class.extend({
    /**
     * @override
     */
    _renderCustomXML(uiFragment) {
        // TODO adapt in master. This sets up a different UI for the image
        // gallery snippet: for this one, we allow to force a specific height
        // in auto mode. It was done in stable as without it, the default height
        // is difficult to understand for the user as it depends on screen
        // height of the one who edited the website and not on the added images.
        // It was also a regression as in <= 11.0, this was a possibility.
        if (this.$target[0].dataset.snippet !== 's_image_gallery') {
            return;
        }
        const minHeightEl = uiFragment.querySelector('we-button-group');
        if (!minHeightEl) {
            return;
        }
        minHeightEl.setAttribute('string', _t("Min-Height"));
        const heightEl = document.createElement('we-input');
        heightEl.setAttribute('string', _t("└ Height"));
        heightEl.dataset.name = 'image_gallery_height_opt';
        heightEl.dataset.unit = 'px';
        heightEl.dataset.selectStyle = '';
        heightEl.dataset.cssProperty = 'height';
        // For this setting, we need to always force the style (= if the block
        // is naturally 800px tall and the user enters 800px for this setting,
        // we set 800px as inline style anyway). Indeed, this snippet's style
        // is based on the height that is forced but once the related public
        // widgets are started, the inner carousel items receive a min-height
        // which makes it so the snippet "natural" height is equal to the
        // initially forced height... so if the style is not forced, it would
        // ultimately be removed by mistake thinking it is not necessary.
        // Note: this is forced as not important as we still need the height to
        // be reset to 'auto' in mobile (generic css rules).
        heightEl.dataset.forceStyle = '';
        uiFragment.appendChild(heightEl);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    /**
     * @override
     */
    _computeWidgetVisibility(widgetName, params) {
<<<<<<< HEAD
        switch (widgetName) {
            case 'no_animation_opt': {
                return !this.isAnimatedText;
            }
            case 'animation_trigger_opt': {
                return !this.$target[0].closest('.dropdown');
            }
            case 'animation_on_scroll_opt':
            case 'animation_direction_opt': {
                return !this.limitedAnimations.some(className => this.$target[0].classList.contains(className));
            }
            case 'animation_intensity_opt': {
                const possibleDirections = this._requestUserValueWidgets('animation_direction_opt')[0].getMethodsParams('selectClass').possibleValues;
                if (this.$target[0].classList.contains('o_anim_fade_in')) {
                    for (const targetClass of this.$target[0].classList) {
                        // Show "Intensity" if "Fade in" + direction is not
                        // "In Place" ...
                        if (possibleDirections.indexOf(targetClass) >= 0) {
                            return true;
                        }
                    }
                    // ... but hide if "Fade in" + "In Place" direction.
                    return false;
                }
                return true;
            }
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    _computeVisibility(methodName, params) {
        if (this.$target[0].matches('img')) {
            return isImageSupportedForStyle(this.$target[0]);
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    _computeWidgetState(methodName, params) {
        if (methodName === 'animationIntensity') {
            return window.getComputedStyle(this.$target[0]).getPropertyValue('--wanim-intensity');
        }
        return this._super(...arguments);
    },
    /**
     * Removes or adds the lazy loading on images because animated images can
     * appear before or after their parents and cause bugs in the animations.
     * To put "lazy" back on the "loading" attribute, we simply remove the
     * attribute as it is automatically added on page load.
     *
     * @private
     * @param {Boolean} lazy
     */
    _toggleImagesLazyLoading(lazy) {
        const imgEls = this.$target[0].matches('img')
            ? [this.$target[0]]
            : this.$target[0].querySelectorAll('img');
        for (const imgEl of imgEls) {
            if (lazy) {
                // Let the automatic system add the loading attribute
                imgEl.removeAttribute('loading');
            } else {
                imgEl.loading = 'eager';
            }
        }
    },
});

/**
 * Replaces current target with the specified template layout
 */
options.registry.MegaMenuLayout = options.registry.SelectTemplate.extend({
    /**
     * @override
     */
    init() {
        this._super(...arguments);
        this.selectTemplateWidgetName = 'mega_menu_template_opt';
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    notify(name, data) {
        if (name === 'reset_template') {
            const xmlid = this._getCurrentTemplateXMLID();
            this._getTemplate(xmlid).then(template => {
                this.containerEl.insertAdjacentHTML('beforeend', template);
                data.onSuccess();
            });
        } else {
            this._super(...arguments);
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeWidgetState: function (methodName, params) {
        if (methodName === 'selectTemplate') {
            return this._getCurrentTemplateXMLID();
        }
        return this._super(...arguments);
    },
    /**
     * @private
     * @returns {string} xmlid of the current template.
     */
    _getCurrentTemplateXMLID: function () {
        const templateDefiningClass = this.containerEl.querySelector('section')
            .classList.value.split(' ').filter(cl => cl.startsWith('s_mega_menu'))[0];
        return `website.${templateDefiningClass}`;
    },
});

/**
 * Hides delete button for Mega Menu block.
 */
options.registry.MegaMenuNoDelete = options.Class.extend({
    forceNoDeleteButton: true,

    /**
     * @override
     */
    async onRemove() {
        await new Promise(resolve => {
            this.trigger_up('option_update', {
                optionName: 'MegaMenuLayout',
                name: 'reset_template',
                data: {
                    onSuccess: () => resolve(),
                }
            });
        });
    },
});

options.registry.sizing.include({
    /**
     * @override
     */
    start() {
        const defs = this._super(...arguments);
        const self = this;
        this.$handles.on('mousedown', function (ev) {
            // Since website is edited in an iframe, a div that goes over the
            // iframe is necessary to catch mousemove and mouseup events,
            // otherwise the iframe absorbs them.
            const $body = $(this.ownerDocument.body);
            if (!self.divEl) {
                self.divEl = document.createElement('div');
                self.divEl.style.position = 'absolute';
                self.divEl.style.height = '100%';
                self.divEl.style.width = '100%';
                self.divEl.setAttribute('id', 'iframeEventOverlay');
                $body.append(self.divEl);
            }
            const documentMouseUp = () => {
                // Multiple mouseup can occur if mouse goes out of the window
                // while moving.
                if (self.divEl) {
                    self.divEl.remove();
                    self.divEl = undefined;
                }
                $body.off('mouseup', documentMouseUp);
            };
            $body.on('mouseup', documentMouseUp);
        });
        return defs;
    }
});

options.registry.SwitchableViews = options.Class.extend({
    /**
     * @override
     */
    async willStart() {
        const _super = this._super.bind(this);
        this.switchableRelatedViews = await new Promise((resolve, reject) => {
            this.trigger_up('get_switchable_related_views', {
                onSuccess: resolve,
                onFailure: reject,
            });
        });
        return _super(...arguments);
    },
    /**
     * @override
     */
    _renderCustomXML(uiFragment) {
        for (const view of this.switchableRelatedViews) {
            const weCheckboxEl = document.createElement('we-checkbox');
            weCheckboxEl.setAttribute('string', view.name);
            weCheckboxEl.setAttribute('data-customize-website-views', view.key);
            weCheckboxEl.setAttribute('data-no-preview', 'true');
            weCheckboxEl.setAttribute('data-reload', '/');
            uiFragment.appendChild(weCheckboxEl);
        }
    },
    /***
     * @override
     */
    _computeVisibility() {
        return !!this.switchableRelatedViews.length;
    },
    /**
     * @override
     */
    _checkIfWidgetsUpdateNeedReload() {
        return true;
    }
});

options.registry.GridImage = options.Class.extend({

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @see this.selectClass for parameters
     */
    changeGridImageMode(previewMode, widgetValue, params) {
        const imageGridItemEl = this._getImageGridItem();
        if (imageGridItemEl) {
            imageGridItemEl.classList.toggle('o_grid_item_image_contain', widgetValue === 'contain');
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Returns the parent column if it is marked as a grid item containing an
     * image.
     *
     * @returns {?HTMLElement}
     */
    _getImageGridItem() {
        const parentEl = this.$target[0].parentNode;
        if (parentEl && parentEl.classList.contains('o_grid_item_image')) {
            return parentEl;
        }
        return null;
    },
    /**
     * @override
     */
    _computeVisibility() {
        return this._super(...arguments)
            && !!this._getImageGridItem()
            && !('shape' in this.$target[0].dataset);
    },
    /**
     * @override
     */
    _computeWidgetState(methodName, params) {
        if (methodName === 'changeGridImageMode') {
            const imageGridItemEl = this._getImageGridItem();
            return imageGridItemEl && imageGridItemEl.classList.contains('o_grid_item_image_contain')
                ? 'contain'
                : 'cover';
        }
        return this._super(...arguments);
    },
});

options.registry.layout_column.include({

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * TODO adapt in master: used to hide the "Layout" options on "Images Wall"
     * (which has its own options to handle the layout).
     *
     * @override
     */
    _computeVisibility() {
        return !this.$target[0].closest('[data-snippet="s_images_wall"]');
=======
        if (widgetName === 'image_gallery_height_opt') {
            return !this.$target[0].classList.contains('o_half_screen_height')
                && !this.$target[0].classList.contains('o_full_screen_height');
        }
        return this._super(...arguments);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
});

return {
    UrlPickerUserValueWidget: UrlPickerUserValueWidget,
    FontFamilyPickerUserValueWidget: FontFamilyPickerUserValueWidget,
};
});
