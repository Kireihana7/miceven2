# Part of Odoo. See LICENSE file for full copyright and licensing details.

import sys
from unittest.mock import patch

from odoo.tests import tagged
from odoo.tools import mute_logger

<<<<<<< HEAD
from odoo.addons.payment.tests.http_common import PaymentHttpCommon
from odoo.addons.payment_stripe.controllers.main import StripeController
from odoo.addons.payment_stripe.tests.common import StripeCommon
=======

class StripeCommon(PaymentAcquirerCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.stripe = cls.env.ref('payment.payment_acquirer_stripe')
        cls.stripe.write({
            'stripe_secret_key': 'sk_test_KJtHgNwt2KS3xM7QJPr4O5E8',
            'stripe_publishable_key': 'pk_test_QSPnimmb4ZhtkEy3Uhdm4S6J',
            'stripe_webhook_secret': 'whsec_vG1fL6CMUouQ7cObF2VJprLVXT5jBLxB',
            'state': 'test',
        })
        cls.token = cls.env['payment.token'].create({
            'name': 'Test Card',
            'acquirer_id': cls.stripe.id,
            'acquirer_ref': 'cus_G27S7FqQ2w3fuH',
            'stripe_payment_method': 'pm_1FW3DdAlCFm536g8eQoSCejY',
            'partner_id': cls.buyer.id,
            'verified': True,
        })
        cls.ideal_icon = cls.env.ref("payment.payment_icon_cc_ideal")
        cls.bancontact_icon = cls.env.ref("payment.payment_icon_cc_bancontact")
        cls.p24_icon = cls.env.ref("payment.payment_icon_cc_p24")
        cls.eps_icon = cls.env.ref("payment.payment_icon_cc_eps")
        cls.giropay_icon = cls.env.ref("payment.payment_icon_cc_giropay")
        cls.all_icons = [cls.ideal_icon, cls.bancontact_icon, cls.p24_icon, cls.eps_icon, cls.giropay_icon]
        cls.stripe.write({'payment_icon_ids': [(5, 0, 0)]})
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe


@tagged('post_install', '-at_install')
class StripeTest(StripeCommon, PaymentHttpCommon):

    def test_processing_values(self):
        dummy_session_id = 'cs_test_sbTG0yGwTszAqFUP8Ulecr1bUwEyQEo29M8taYvdP7UA6Qr37qX6uA6w'
        tx = self._create_transaction(flow='redirect')  # We don't really care what the flow is here.

        # Ensure no external API call is done, we only want to check the processing values logic
        def mock_stripe_create_checkout_session(self):
            return {'id': dummy_session_id}

        with patch.object(
            type(self.env['payment.transaction']), '_stripe_create_checkout_session',
            mock_stripe_create_checkout_session,
        ), mute_logger('odoo.addons.payment.models.payment_transaction'):
            processing_values = tx._get_processing_values()

        self.assertEqual(processing_values['publishable_key'], self.stripe.stripe_publishable_key)
        self.assertEqual(processing_values['session_id'], dummy_session_id)

    @mute_logger('odoo.addons.payment_stripe.models.payment_transaction')
    def test_tx_state_after_send_capture_request(self):
        self.provider.capture_manually = True
        tx = self._create_transaction('redirect', state='authorized')

        with patch(
            'odoo.addons.payment_stripe.models.payment_provider.PaymentProvider'
            '._stripe_make_request',
            return_value={'status': 'succeeded'},
        ):
            tx._send_capture_request()
        self.assertEqual(
            tx.state, 'done', msg="The state should be 'done' after a successful capture."
        )

    @mute_logger('odoo.addons.payment_stripe.models.payment_transaction')
    def test_tx_state_after_send_void_request(self):
        self.provider.capture_manually = True
        tx = self._create_transaction('redirect', state='authorized')

        with patch(
            'odoo.addons.payment_stripe.models.payment_provider.PaymentProvider'
            '._stripe_make_request',
            return_value={'status': 'canceled'},
        ):
            tx._send_void_request()
        self.assertEqual(
            tx.state, 'cancel', msg="The state should be 'cancel' after voiding the transaction."
        )

<<<<<<< HEAD
    @mute_logger('odoo.addons.payment_stripe.controllers.main')
    def test_webhook_notification_confirms_transaction(self):
        """ Test the processing of a webhook notification. """
        tx = self._create_transaction('redirect')
        url = self._build_url(StripeController._webhook_url)
        with patch(
            'odoo.addons.payment_stripe.controllers.main.StripeController'
            '._verify_notification_signature'
        ):
            self._make_json_request(url, data=self.notification_data)
        self.assertEqual(tx.state, 'done')

    @mute_logger('odoo.addons.payment_stripe.controllers.main')
    def test_webhook_notification_tokenizes_payment_method(self):
        """ Test the processing of a webhook notification. """
        self._create_transaction('dummy', operation='validation', tokenize=True)
        url = self._build_url(StripeController._webhook_url)
        payment_method_response = {
            'card': {'last4': '4242'},
            'id': 'pm_1KVZSNAlCFm536g8sYB92I1G',
            'type': 'card'
=======
    def test_add_available_payment_method_types_local_enabled(self):
        self.stripe.payment_icon_ids = [(6, 0, [i.id for i in self.all_icons])]
        tx_values = {
            'billing_partner_country': self.env.ref('base.be'),
            'currency': self.env.ref('base.EUR'),
            'type': 'form'
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        with patch(
            'odoo.addons.payment_stripe.controllers.main.StripeController'
            '._verify_notification_signature'
        ), patch(
            'odoo.addons.payment_stripe.models.payment_provider.PaymentProvider'
            '._stripe_make_request',
            return_value=payment_method_response,
        ), patch(
            'odoo.addons.payment_stripe.models.payment_transaction.PaymentTransaction'
            '._stripe_tokenize_from_notification_data'
        ) as tokenize_check_mock:
            self._make_json_request(
                url, data=dict(self.notification_data, type="setup_intent.succeeded")
            )
        self.assertEqual(tokenize_check_mock.call_count, 1)

    @mute_logger('odoo.addons.payment_stripe.controllers.main')
    def test_webhook_notification_triggers_signature_check(self):
        """ Test that receiving a webhook notification triggers a signature check. """
        self._create_transaction('redirect')
        url = self._build_url(StripeController._webhook_url)
        with patch(
            'odoo.addons.payment_stripe.controllers.main.StripeController'
            '._verify_notification_signature'
        ) as signature_check_mock, patch(
            'odoo.addons.payment.models.payment_transaction.PaymentTransaction'
            '._handle_notification_data'
        ):
            self._make_json_request(url, data=self.notification_data)
            self.assertEqual(signature_check_mock.call_count, 1)

    def test_onboarding_action_redirect_to_url(self):
        """ Test that the action generate and return an URL when the provider is disabled. """
        with patch.object(
            type(self.env['payment.provider']), '_stripe_fetch_or_create_connected_account',
            return_value={'id': 'dummy'},
        ), patch.object(
            type(self.env['payment.provider']), '_stripe_create_account_link',
            return_value='https://dummy.url',
        ):
            onboarding_url = self.stripe.action_stripe_connect_account()
        self.assertEqual(onboarding_url['url'], 'https://dummy.url')

<<<<<<< HEAD
    def test_only_create_webhook_if_not_already_done(self):
        """ Test that a webhook is created only if the webhook secret is not already set. """
        self.stripe.stripe_webhook_secret = False
        with patch.object(type(self.env['payment.provider']), '_stripe_make_request') as mock:
            self.stripe.action_stripe_create_webhook()
            self.assertEqual(mock.call_count, 1)
=======
    def test_add_available_payment_method_types_local_enabled_2(self):
        self.stripe.payment_icon_ids = [(6, 0, [i.id for i in self.all_icons])]
        tx_values = {
            'billing_partner_country': self.env.ref('base.pl'),
            'currency': self.env.ref('base.PLN'),
            'type': 'form'
        }
        stripe_session_data = {}

        self.stripe._add_available_payment_method_types(stripe_session_data, tx_values)

        actual = {pmt for key, pmt in stripe_session_data.items() if key.startswith('payment_method_types')}
        self.assertEqual({'card', 'p24'}, actual)

    def test_add_available_payment_method_types_pmt_does_not_exist(self):
        self.bancontact_icon.unlink()
        tx_values = {
            'billing_partner_country': self.env.ref('base.be'),
            'currency': self.env.ref('base.EUR'),
            'type': 'form'
        }
        stripe_session_data = {}

        self.stripe._add_available_payment_method_types(stripe_session_data, tx_values)

        actual = {pmt for key, pmt in stripe_session_data.items() if key.startswith('payment_method_types')}
        self.assertEqual({'card', 'bancontact'}, actual)

    def test_add_available_payment_method_types_local_disabled(self):
        tx_values = {
            'billing_partner_country': self.env.ref('base.be'),
            'currency': self.env.ref('base.EUR'),
            'type': 'form'
        }
        stripe_session_data = {}

        self.stripe._add_available_payment_method_types(stripe_session_data, tx_values)

        actual = {pmt for key, pmt in stripe_session_data.items() if key.startswith('payment_method_types')}
        self.assertEqual({'card'}, actual)

    def test_add_available_payment_method_types_local_all_but_bancontact(self):
        self.stripe.payment_icon_ids = [(4, icon.id) for icon in self.all_icons if icon.name.lower() != 'bancontact']
        tx_values = {
            'billing_partner_country': self.env.ref('base.be'),
            'currency': self.env.ref('base.EUR'),
            'type': 'form'
        }
        stripe_session_data = {}

        self.stripe._add_available_payment_method_types(stripe_session_data, tx_values)

        actual = {pmt for key, pmt in stripe_session_data.items() if key.startswith('payment_method_types')}
        self.assertEqual({'card'}, actual)

    def test_add_available_payment_method_types_recurrent(self):
        tx_values = {
            'billing_partner_country': self.env.ref('base.be'),
            'currency': self.env.ref('base.EUR'),
            'type': 'form_save'
        }
        stripe_session_data = {}
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    def test_do_not_create_webhook_if_already_done(self):
        """ Test that no webhook is created if the webhook secret is already set. """
        self.stripe.stripe_webhook_secret = 'dummy'
        with patch.object(type(self.env['payment.provider']), '_stripe_make_request') as mock:
            self.stripe.action_stripe_create_webhook()
            self.assertEqual(mock.call_count, 0)

<<<<<<< HEAD
    def test_create_account_link_pass_required_parameters(self):
        """ Test that the generation of an account link includes all the required parameters. """
        with patch.object(
            type(self.env['payment.provider']), '_stripe_make_proxy_request',
            return_value={'url': 'https://dummy.url'},
        ) as mock:
            self.stripe._stripe_create_account_link('dummy', 'dummy')
            mock.assert_called_once()
            if sys.version_info >= (3, 8):
                # call_args.kwargs is only available in python 3.8+
                call_args = mock.call_args.kwargs['payload'].keys()
                for payload_param in ('account', 'return_url', 'refresh_url', 'type'):
                    self.assertIn(payload_param, call_args)
=======
        actual = {pmt for key, pmt in stripe_session_data.items() if key.startswith('payment_method_types')}
        self.assertEqual({'card'}, actual)

    def test_discarded_webhook(self):
        self.assertFalse(self.env['payment.acquirer']._handle_stripe_webhook(dict(type='payment.intent.succeeded')))

    def test_handle_checkout_webhook_no_secret(self):
        self.stripe.stripe_webhook_secret = None

        with self.assertRaises(ValidationError):
            self.env['payment.acquirer']._handle_stripe_webhook(dict(type='checkout.session.completed'))

    @patch('odoo.addons.payment_stripe.models.payment.request')
    @patch('odoo.addons.payment_stripe.models.payment.datetime')
    def test_handle_checkout_webhook(self, dt, request):
        # pass signature verification
        dt.utcnow.return_value.timestamp.return_value = 1591264652
        request.httprequest.headers = {'Stripe-Signature': stripe_mocks.checkout_session_signature}
        request.httprequest.data = stripe_mocks.checkout_session_body
        # test setup
        tx = self.env['payment.transaction'].create({
            'reference': 'tx_ref_test_handle_checkout_webhook',
            'currency_id': self.currency_euro.id,
            'acquirer_id': self.stripe.id,
            'partner_id': self.buyer_id,
            'payment_token_id': self.token.id,
            'type': 'server2server',
            'amount': 30
        })
        res = tx.with_context(off_session=True)._stripe_create_payment_intent()
        tx.stripe_payment_intent = res.get('payment_intent')
        stripe_object = stripe_mocks.checkout_session_object

        actual = self.stripe._handle_checkout_webhook(stripe_object)

        self.assertTrue(actual)

    @patch('odoo.addons.payment_stripe.models.payment.request')
    @patch('odoo.addons.payment_stripe.models.payment.datetime')
    def test_handle_checkout_webhook_wrong_amount(self, dt, request):
        # pass signature verification
        dt.utcnow.return_value.timestamp.return_value = 1591264652
        request.httprequest.headers = {'Stripe-Signature': stripe_mocks.checkout_session_signature}
        request.httprequest.data = stripe_mocks.checkout_session_body
        # test setup
        bad_tx = self.env['payment.transaction'].create({
            'reference': 'tx_ref_test_handle_checkout_webhook_wrong_amount',
            'currency_id': self.currency_euro.id,
            'acquirer_id': self.stripe.id,
            'partner_id': self.buyer_id,
            'payment_token_id': self.token.id,
            'type': 'server2server',
            'amount': 10
        })
        wrong_amount_stripe_payment_intent = bad_tx.with_context(off_session=True)._stripe_create_payment_intent()
        tx = self.env['payment.transaction'].create({
            'reference': 'tx_ref_test_handle_checkout_webhook',
            'currency_id': self.currency_euro.id,
            'acquirer_id': self.stripe.id,
            'partner_id': self.buyer_id,
            'payment_token_id': self.token.id,
            'type': 'server2server',
            'amount': 30
        })
        tx.stripe_payment_intent = wrong_amount_stripe_payment_intent.get('payment_intent')
        stripe_object = stripe_mocks.checkout_session_object

        actual = self.env['payment.acquirer']._handle_checkout_webhook(stripe_object)

        self.assertFalse(actual)

    def test_handle_checkout_webhook_no_odoo_tx(self):
        stripe_object = stripe_mocks.checkout_session_object

        actual = self.stripe._handle_checkout_webhook(stripe_object)

        self.assertFalse(actual)

    @patch('odoo.addons.payment_stripe.models.payment.request')
    @patch('odoo.addons.payment_stripe.models.payment.datetime')
    def test_handle_checkout_webhook_no_stripe_tx(self, dt, request):
        # pass signature verification
        dt.utcnow.return_value.timestamp.return_value = 1591264652
        request.httprequest.headers = {'Stripe-Signature': stripe_mocks.checkout_session_signature}
        request.httprequest.data = stripe_mocks.checkout_session_body
        # test setup
        self.env['payment.transaction'].create({
            'reference': 'tx_ref_test_handle_checkout_webhook',
            'currency_id': self.currency_euro.id,
            'acquirer_id': self.stripe.id,
            'partner_id': self.buyer_id,
            'payment_token_id': self.token.id,
            'type': 'server2server',
            'amount': 30
        })
        stripe_object = stripe_mocks.checkout_session_object

        with self.assertRaises(ValidationError):
            self.stripe._handle_checkout_webhook(stripe_object)

    @patch('odoo.addons.payment_stripe.models.payment.request')
    @patch('odoo.addons.payment_stripe.models.payment.datetime')
    def test_verify_stripe_signature(self, dt, request):
        dt.utcnow.return_value.timestamp.return_value = 1591264652
        request.httprequest.headers = {'Stripe-Signature': stripe_mocks.checkout_session_signature}
        request.httprequest.data = stripe_mocks.checkout_session_body

        actual = self.stripe._verify_stripe_signature()

        self.assertTrue(actual)

    @patch('odoo.addons.payment_stripe.models.payment.request')
    @patch('odoo.addons.payment_stripe.models.payment.datetime')
    def test_verify_stripe_signature_tampered_body(self, dt, request):
        dt.utcnow.return_value.timestamp.return_value = 1591264652
        request.httprequest.headers = {'Stripe-Signature': stripe_mocks.checkout_session_signature}
        request.httprequest.data = stripe_mocks.checkout_session_body.replace(b'1500', b'10')

        with self.assertRaises(ValidationError):
            self.stripe._verify_stripe_signature()

    @patch('odoo.addons.payment_stripe.models.payment.request')
    @patch('odoo.addons.payment_stripe.models.payment.datetime')
    def test_verify_stripe_signature_wrong_secret(self, dt, request):
        dt.utcnow.return_value.timestamp.return_value = 1591264652
        request.httprequest.headers = {'Stripe-Signature': stripe_mocks.checkout_session_signature}
        request.httprequest.data = stripe_mocks.checkout_session_body
        self.stripe.write({
            'stripe_webhook_secret': 'whsec_vG1fL6CMUouQ7cObF2VJprL_TAMPERED',
        })

        with self.assertRaises(ValidationError):
            self.stripe._verify_stripe_signature()

    @patch('odoo.addons.payment_stripe.models.payment.request')
    @patch('odoo.addons.payment_stripe.models.payment.datetime')
    def test_verify_stripe_signature_too_old(self, dt, request):
        dt.utcnow.return_value.timestamp.return_value = 1591264652 + STRIPE_SIGNATURE_AGE_TOLERANCE + 1
        request.httprequest.headers = {'Stripe-Signature': stripe_mocks.checkout_session_signature}
        request.httprequest.data = stripe_mocks.checkout_session_body

        with self.assertRaises(ValidationError):
            self.stripe._verify_stripe_signature()
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
