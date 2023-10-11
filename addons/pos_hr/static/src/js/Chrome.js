odoo.define('pos_hr.chrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const PosHrChrome = (Chrome) =>
        class extends Chrome {
            async start() {
                await super.start();
                if (this.env.pos.config.module_pos_hr) this.showTempScreen('LoginScreen');
            }
            get headerButtonIsShown() {
<<<<<<< HEAD
                return !this.env.pos.config.module_pos_hr || this.env.pos.get_cashier().role == 'manager' || this.env.pos.get_cashier_user_id() === this.env.pos.user.id;
            }
            showCashMoveButton() {
                return super.showCashMoveButton() && (!this.env.pos.cashier || this.env.pos.cashier.role == 'manager');
            }
            shouldShowCashControl() {
                if (this.env.pos.config.module_pos_hr){
                    return super.shouldShowCashControl() && this.env.pos.hasLoggedIn;
                }
                return super.shouldShowCashControl();
=======
                return !this.env.pos.config.module_pos_hr || this.env.pos.get('cashier').role == 'manager';
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
        };

    Registries.Component.extend(Chrome, PosHrChrome);

    return Chrome;
});
