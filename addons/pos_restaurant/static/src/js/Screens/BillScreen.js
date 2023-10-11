odoo.define('pos_restaurant.BillScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const BillScreen = (ReceiptScreen) => {
        class BillScreen extends ReceiptScreen {
            confirm() {
                this.props.resolve({ confirmed: true, payload: null });
                this.trigger('close-temp-screen');
            }
            whenClosing() {
                this.confirm();
            }
            /**
             * @override
             */
            async printReceipt() {
                await super.printReceipt();
                this.currentOrder._printed = false;
<<<<<<< HEAD
                if (this.env.pos.config.iface_print_skip_screen && !this.env.isMobile) {
                    this.confirm();
                }
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
        }
        BillScreen.template = 'BillScreen';
        return BillScreen;
    };

    Registries.Component.addByExtending(BillScreen, ReceiptScreen);

    return BillScreen;
});
