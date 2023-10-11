odoo.define('l10n_gcc_pos.OrderReceipt', function (require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt')
    const Registries = require('point_of_sale.Registries');

    const OrderReceiptGCC = OrderReceipt =>
        class extends OrderReceipt {

            get receiptEnv() {
                let receipt_render_env = super.receiptEnv;
                let receipt = receipt_render_env.receipt;
<<<<<<< HEAD
                const country = receipt_render_env.order.pos.company.country;
                receipt.is_gcc_country =  country ? ['SA', 'AE', 'BH', 'OM', 'QA', 'KW'].includes(country && country.code) : false;
=======
                let company = this.env.pos.company;
                receipt.is_gcc_country = company.country ? ['SA', 'AE', 'BH', 'OM', 'QA', 'KW'].includes(company.country.code) : false;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                return receipt_render_env;
            }
        }
    Registries.Component.extend(OrderReceipt, OrderReceiptGCC)
    return OrderReceiptGCC
});
