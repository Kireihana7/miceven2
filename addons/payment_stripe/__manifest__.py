# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Provider: Stripe',
    'version': '2.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "An Irish-American payment provider covering the US and many others.",
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_stripe_templates.xml',
        'views/payment_templates.xml',  # Only load the SDK on pages with a payment form.

        'data/payment_provider_data.xml',  # Depends on views/payment_stripe_templates.xml
    ],
    'application': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
<<<<<<< HEAD
    'assets': {
        'web.assets_frontend': [
            'payment_stripe/static/src/js/express_checkout_form.js',
            'payment_stripe/static/src/js/payment_form.js',
            'payment_stripe/static/src/js/stripe_options.js',
        ],
    },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    'license': 'LGPL-3',
}
