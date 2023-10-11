odoo.define('mass_mailing.website_integration', function (require) {
"use strict";

var core = require('web.core');
<<<<<<< HEAD
=======
const dom = require('web.dom');
var Dialog = require('web.Dialog');
var utils = require('web.utils');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
var publicWidget = require('web.public.widget');
const session = require('web.session');

// FIXME the 14.0 was released with this but without the google_recaptcha
// module being added as a dependency of the website_mass_mailing module. This
// is to be fixed in master of course but in stable, we'll have to use a
// workaround.
// const {ReCaptcha} = require('google_recaptcha.ReCaptchaV3');

var _t = core._t;

let alertReCaptchaDisplayed;

publicWidget.registry.subscribe = publicWidget.Widget.extend({
    selector: ".js_subscribe",
    disabledInEditableMode: false,
    read_events: {
        'click .js_subscribe_btn': '_onSubscribeClick',
    },

    /**
     * @constructor
     */
    init: function () {
        this._super(...arguments);
        const ReCaptchaService = odoo.__DEBUG__.services['google_recaptcha.ReCaptchaV3'];
        this._recaptcha = ReCaptchaService && new ReCaptchaService.ReCaptcha() || null;
    },
    /**
     * @override
     */
    willStart: function () {
        if (this._recaptcha) {
            this._recaptcha.loadLibs();
        }
        return this._super(...arguments);
    },
    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);

<<<<<<< HEAD
        if (this.editableMode) {
            // Since there is an editor option to choose whether "Thanks" button
            // should be visible or not, we should not vary its visibility here.
            return def;
        }
        const always = this._updateView.bind(this);
        const inputName = this.$target[0].querySelector('input').name;
=======
        if (!this._recaptcha && this.editableMode && session.is_admin && !alertReCaptchaDisplayed) {
            this.displayNotification({
                type: 'info',
                message: _t("Do you want to install Google reCAPTCHA to secure your newsletter subscriptions?"),
                sticky: true,
                buttons: [{text: _t("Install now"), primary: true, click: async () => {
                    dom.addButtonLoadingEffect($('.o_notification .btn-primary')[0]);

                    const record = await this._rpc({
                        model: 'ir.module.module',
                        method: 'search_read',
                        domain: [['name', '=', 'google_recaptcha']],
                        fields: ['id'],
                        limit: 1,
                    });
                    await this._rpc({
                        model: 'ir.module.module',
                        method: 'button_immediate_install',
                        args: [[record[0]['id']]],
                    });

                    this.displayNotification({
                        type: 'info',
                        message: _t("Google reCAPTCHA is now installed! You can configure it from your website settings."),
                        sticky: true,
                        buttons: [{text: _t("Website settings"), primary: true, click: async () => {
                            window.open('/web#action=website.action_website_configuration', '_blank');
                        }}],
                    });
                }}],
            });
            alertReCaptchaDisplayed = true;
        }

        this.$popup = this.$target.closest('.o_newsletter_modal');
        if (this.$popup.length) {
            // No need to check whether the user subscribed or not if the input
            // is in a popup as the popup won't open if he did subscribe.
            return def;
        }

        if (this.editableMode) {
            // Since there is an editor option to choose whether "Thanks" button
            // should be visible or not, we should not vary its visibility here.
            return def;
        }
        const always = this._updateView.bind(this);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        return Promise.all([def, this._rpc({
            route: '/website_mass_mailing/is_subscriber',
            params: {
                'list_id': this._getListId(),
                'subscription_type': inputName,
            },
        }).then(always).guardedCatch(always)]);
    },
    /**
     * @override
     */
    destroy() {
        this._updateView({is_subscriber: false});
        this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Modifies the elements to have the view of a subscriber/non-subscriber.
     *
     * @param {Object} data
     */
    _updateView(data) {
        const isSubscriber = data.is_subscriber;
        const subscribeBtnEl = this.$target[0].querySelector('.js_subscribe_btn');
        const thanksBtnEl = this.$target[0].querySelector('.js_subscribed_btn');
<<<<<<< HEAD
        const valueInputEl = this.$target[0].querySelector('input.js_subscribe_value, input.js_subscribe_email'); // js_subscribe_email is kept by compatibility (it was the old name of js_subscribe_value)

        subscribeBtnEl.disabled = isSubscriber;
        valueInputEl.value = data.value || '';
        valueInputEl.disabled = isSubscriber;
=======
        const emailInputEl = this.$target[0].querySelector('input.js_subscribe_email');

        subscribeBtnEl.disabled = isSubscriber;
        emailInputEl.value = data.email || '';
        emailInputEl.disabled = isSubscriber;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        // Compat: remove d-none for DBs that have the button saved with it.
        this.$target[0].classList.remove('d-none');

        subscribeBtnEl.classList.toggle('d-none', !!isSubscriber);
        thanksBtnEl.classList.toggle('d-none', !isSubscriber);
    },
<<<<<<< HEAD

    _getListId: function () {
        return this.$target.closest('[data-snippet=s_newsletter_block').data('list-id') || this.$target.data('list-id');
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onSubscribeClick: async function () {
        var self = this;
        const inputName = this.$('input').attr('name');
        const $input = this.$(".js_subscribe_value:visible, .js_subscribe_email:visible"); // js_subscribe_email is kept by compatibility (it was the old name of js_subscribe_value)
        if (inputName === 'email' && $input.length && !$input.val().match(/.+@.+/)) {
            this.$target.addClass('o_has_error').find('.form-control').addClass('is-invalid');
            return false;
        }
        this.$target.removeClass('o_has_error').find('.form-control').removeClass('is-invalid');
<<<<<<< HEAD
        const tokenObj = await this._recaptcha.getToken('website_mass_mailing_subscribe');
        if (tokenObj.error) {
            self.displayNotification({
                type: 'danger',
                title: _t("Error"),
                message: tokenObj.error,
                sticky: true,
            });
            return false;
        }
        this._rpc({
            route: '/website_mass_mailing/subscribe',
            params: {
                'list_id': this._getListId(),
                'value': $input.length ? $input.val() : false,
                'subscription_type': inputName,
                recaptcha_token_response: tokenObj.token,
            },
=======
        let tokenObj = null;
        if (this._recaptcha) {
            tokenObj = await this._recaptcha.getToken('website_mass_mailing_subscribe');
            if (tokenObj.error) {
                self.displayNotification({
                    type: 'danger',
                    title: _t("Error"),
                    message: tokenObj.error,
                    sticky: true,
                });
                return false;
            }
        }
        const params = {
            'list_id': this.$target.data('list-id'),
            'email': $email.length ? $email.val() : false,
        };
        if (this._recaptcha) {
            params['recaptcha_token_response'] = tokenObj.token;
        }
        this._rpc({
            route: '/website_mass_mailing/subscribe',
            params: params,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }).then(function (result) {
            let toastType = result.toast_type;
            if (toastType === 'success') {
                self.$(".js_subscribe_btn").addClass('d-none');
                self.$(".js_subscribed_btn").removeClass('d-none');
                self.$('input.js_subscribe_value, input.js_subscribe_email').prop('disabled', !!result); // js_subscribe_email is kept by compatibility (it was the old name of js_subscribe_value)
                const $popup = self.$target.closest('.o_newsletter_modal');
                if ($popup.length) {
                    $popup.modal('hide');
                }
            }
            self.displayNotification({
                type: toastType,
                title: toastType === 'success' ? _t('Success') : _t('Error'),
                message: result.toast_content,
                sticky: true,
            });
        });
    },
});

/**
 * This widget tries to fix snippets that were malformed because of a missing
 * upgrade script. Without this, some newsletter snippets coming from users
 * upgraded from a version lower than 16.0 may not be able to update their
 * newsletter block.
 *
 * TODO an upgrade script should be made to fix databases and get rid of this.
 */
publicWidget.registry.fixNewsletterListClass = publicWidget.Widget.extend({
    selector: '.s_newsletter_subscribe_form:not(.s_subscription_list), .s_newsletter_block',

    /**
     * @override
     */
    start() {
        this.$target[0].classList.add('s_newsletter_list');
        return this._super(...arguments);
    },
});

});
