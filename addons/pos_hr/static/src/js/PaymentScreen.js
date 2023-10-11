odoo.define('pos_hr.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PosHrPaymentScreen = (PaymentScreen_) =>
          class extends PaymentScreen_ {
              async _finalizeValidation() {
<<<<<<< HEAD
                  this.currentOrder.cashier = this.env.pos.get_cashier();
=======
                  this.currentOrder.employee = this.env.pos.get_cashier();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                  await super._finalizeValidation();
              }
          };

    Registries.Component.extend(PaymentScreen, PosHrPaymentScreen);

    return PaymentScreen;
});
