/** @odoo-module */
/* global Stripe */

import checkoutForm from 'payment.checkout_form';
import manageForm from 'payment.manage_form';
import { StripeOptions } from '@payment_stripe/js/stripe_options';

const stripeMixin = {

     /**
     * called to create payment method object for credit card/debit card.
     *
     * @private
     * @param {Object} stripe
     * @param {Object} formData
     * @param {Object} card
     * @param {Boolean} addPmEvent
     * @returns {Promise}
     */
    _createPaymentMethod: function (stripe, formData, card, addPmEvent) {
        if (addPmEvent) {
            return this._rpc({
                route: '/payment/stripe/s2s/create_setup_intent',
                params: {'acquirer_id': formData.acquirer_id}
            }).then(function(intent_secret) {
                return stripe.handleCardSetup(intent_secret, card);
            });
        } else {
            return stripe.createPaymentMethod({
                type: 'card',
                card: card,
            });
        }
    },

    /**
     * Redirect the customer to Stripe hosted payment page.
     *
     * @override method from payment.payment_form_mixin
     * @private
     * @param {string} code - The code of the payment option
     * @param {number} paymentOptionId - The id of the payment option handling the transaction
     * @param {object} processingValues - The processing values of the transaction
     * @return {undefined}
     */
    _processRedirectPayment: function (code, paymentOptionId, processingValues) {
        if (code !== 'stripe') {
            return this._super(...arguments);
        }

<<<<<<< HEAD
        const stripeJS = Stripe(
            processingValues['publishable_key'],
            // Instantiate the StripeOptions class to allow patching the method and add options.
            new StripeOptions()._prepareStripeOptions(processingValues),
        );
        stripeJS.redirectToCheckout({
            sessionId: processingValues['session_id']
        });
    },
};
=======
        var formData = self.getFormData(inputsForm);
        var stripe = this.stripe;
        var card = this.stripe_card_element;
        if (card._invalid) {
            // if we don't enable the button again, at this point the button is displaying the 'loading' animation
            // and since we break the workflow here it gives the impression that something is happening, but it isn't
            self.enableButton(button);
            return;
        }
        this._createPaymentMethod(stripe, formData, card, addPmEvent).then(function(result) {
            if (result.error) {
                return Promise.reject({"message": {"data": { "arguments": [result.error.message]}}});
            } else {
                const paymentMethod = addPmEvent ? result.setupIntent.payment_method : result.paymentMethod.id;
                _.extend(formData, {"payment_method": paymentMethod});
                return self._rpc({
                    route: formData.data_set,
                    params: formData,
                });
            }
        }).then(function(result) {
            if (addPmEvent) {
                if (formData.return_url) {
                    window.location = formData.return_url;
                } else {
                    window.location.reload();
                }
            } else {
                $checkedRadio.val(result.id);
                self.el.submit();
            }
        }).guardedCatch(function (error) {
            // We don't want to open the Error dialog since
            // we already have a container displaying the error
            if (error.event) {
                error.event.preventDefault();
            }
            // if the rpc fails, pretty obvious
            self.enableButton(button);
            self.displayError(
                _t('Unable to save card'),
                _t("We are not able to add your payment method at the moment. ") +
                    self._parseError(error)
            );
        });
    },
    /**
     * called when clicking a Stripe radio if configured for s2s flow; instanciates the card and bind it to the widget.
     *
     * @private
     * @param {DOMElement} checkedRadio
     */
    _bindStripeCard: function ($checkedRadio) {
        var acquirerID = this.getAcquirerIdFromRadio($checkedRadio);
        var acquirerForm = this.$('#o_payment_add_token_acq_' + acquirerID);
        var inputsForm = $('input', acquirerForm);
        var formData = this.getFormData(inputsForm);
        var stripe = Stripe(formData.stripe_publishable_key);
        var element = stripe.elements();
        var card = element.create('card', {hidePostalCode: true});
        // use more specific css selector so that '#card-element' is found inside the selected stripe card, otherwise
        // this won't happen, and the card will be mounted to the first element found.
        card.mount(`#o_payment_add_token_acq_${acquirerID} #card-element`);
        card.on('ready', function(ev) {
            card.focus();
        });
        card.addEventListener('change', function (event) {
            var displayError = document.getElementById('card-errors');
            displayError.textContent = '';
            if (event.error) {
                displayError.textContent = event.error.message;
            }
        });
        this.stripe = stripe;
        this.stripe_card_element = card;
    },
    /**
     * destroys the card element and any stripe instance linked to the widget.
     *
     * @private
     */
    _unbindStripeCard: function () {
        if (this.stripe_card_element) {
            this.stripe_card_element.destroy();
        }
        this.stripe = undefined;
        this.stripe_card_element = undefined;
    },
    /**
     * @override
     */
    updateNewPaymentDisplayStatus: function () {
        var $checkedRadio = this.$('input[type="radio"]:checked');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

checkoutForm.include(stripeMixin);
manageForm.include(stripeMixin);
