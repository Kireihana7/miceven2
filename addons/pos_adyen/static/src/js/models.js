odoo.define('pos_adyen.models', function (require) {
const { register_payment_method, Payment } = require('point_of_sale.models');
const PaymentAdyen = require('pos_adyen.payment');
const Registries = require('point_of_sale.Registries');

<<<<<<< HEAD
register_payment_method('adyen', PaymentAdyen);

const PosAdyenPayment = (Payment) => class PosAdyenPayment extends Payment {
    constructor(obj, options) {
        super(...arguments);
        this.terminalServiceId = this.terminalServiceId || null;
    }
    //@override
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.terminal_service_id = this.terminalServiceId;
        return json;
    }
    //@override
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.terminalServiceId = json.terminal_service_id;
    }
    setTerminalServiceId(id) {
        this.terminalServiceId = id;
    }
}
Registries.Model.extend(Payment, PosAdyenPayment);
=======
models.register_payment_method('adyen', PaymentAdyen);
models.register_payment_method('odoo_adyen', PaymentAdyen);
models.load_fields('pos.payment.method', 'adyen_terminal_identifier');

const superPaymentline = models.Paymentline.prototype;
models.Paymentline = models.Paymentline.extend({
    initialize: function(attr, options) {
        superPaymentline.initialize.call(this,attr,options);
        this.terminalServiceId = this.terminalServiceId  || null;
    },
    export_as_JSON: function(){
        const json = superPaymentline.export_as_JSON.call(this);
        json.terminal_service_id = this.terminalServiceId;
        return json;
    },
    init_from_JSON: function(json){
        superPaymentline.init_from_JSON.apply(this,arguments);
        this.terminalServiceId = json.terminal_service_id;
    },
    setTerminalServiceId: function(id) {
        this.terminalServiceId = id;
    }
});

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
});
