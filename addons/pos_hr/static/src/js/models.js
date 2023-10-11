odoo.define('pos_hr.employees', function (require) {
    "use strict";

var { PosGlobalState, Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');

<<<<<<< HEAD

const PosHrPosGlobalState = (PosGlobalState) => class PosHrPosGlobalState extends PosGlobalState {
    async _processData(loadedData) {
        await super._processData(...arguments);
        if (this.config.module_pos_hr) {
            this.employees = loadedData['hr.employee'];
            this.employee_by_id = loadedData['employee_by_id'];
            this.reset_cashier();
        }
    }
    async after_load_server_data() {
        await super.after_load_server_data(...arguments);
        if (this.config.module_pos_hr) {
            this.hasLoggedIn = !this.config.module_pos_hr;
        }
    }
    reset_cashier() {
        this.cashier = {name: null, id: null, barcode: null, user_id: null, pin: null, role: null};
    }
    set_cashier(employee) {
        this.cashier = employee;
        const selectedOrder = this.get_order();
        if (selectedOrder && !selectedOrder.get_orderlines().length) {
            // Order without lines can be considered to be un-owned by any employee.
            // We set the cashier on that order to the currently set employee.
            selectedOrder.cashier = employee;
        }
        if (!this.cashierHasPriceControlRights() && this.numpadMode === 'price') {
            this.numpadMode = 'quantity';
=======
models.load_models([{
    model:  'hr.employee',
    fields: ['name', 'id', 'user_id'],
    domain: function(self){
        return self.config.employee_ids.length > 0
            ? [
                  '&',
                  ['company_id', '=', self.config.company_id[0]],
                  '|',
                  ['user_id', '=', self.user.id],
                  ['id', 'in', self.config.employee_ids],
              ]
            : [['company_id', '=', self.config.company_id[0]]];
    },
    loaded: function(self, employees) {
        if (self.config.module_pos_hr) {
            self.employees = employees;
            self.employee_by_id = {};
            self.employees.forEach(function(employee) {
                self.employee_by_id[employee.id] = employee;
                var hasUser = self.users.some(function(user) {
                    if (user.id === employee.user_id[0]) {
                        employee.role = user.role;
                        return true;
                    }
                    return false;
                });
                if (!hasUser) {
                    employee.role = 'cashier';
                }
            });
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
    }

<<<<<<< HEAD
    /**{name: null, id: null, barcode: null, user_id:null, pin:null}
     * If pos_hr is activated, return {name: string, id: int, barcode: string, pin: string, user_id: int}
     * @returns {null|*}
     */
    get_cashier() {
        if (this.config.module_pos_hr) {
            return this.cashier;
        }
        return super.get_cashier();
    }
    get_cashier_user_id() {
        if (this.config.module_pos_hr) {
            return this.cashier.user_id ? this.cashier.user_id : null;
        }
        return super.get_cashier_user_id();
    }
}
Registries.Model.extend(PosGlobalState, PosHrPosGlobalState);


const PosHrOrder = (Order) => class PosHrOrder extends Order {
    constructor(obj, options) {
        super(...arguments);
        if (!options.json && this.pos.config.module_pos_hr) {
            this.cashier = this.pos.get_cashier();
        }
    }
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if (this.pos.config.module_pos_hr && json.employee_id) {
            this.cashier = this.pos.employee_by_id[json.employee_id];
        }
    }
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        if (this.pos.config.module_pos_hr) {
            json.employee_id = this.cashier ? this.cashier.id : false;
        }
        return json;
    }
}
Registries.Model.extend(Order, PosHrOrder);
=======
var posmodel_super = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
    load_server_data: function () {
        var self = this;
        return posmodel_super.load_server_data.apply(this, arguments).then(function () {
            var employee_ids = _.map(self.employees, function(employee){return employee.id;});
            var records = self.rpc({
                model: 'hr.employee',
                method: 'get_barcodes_and_pin_hashed',
                args: [employee_ids],
            });
            return records.then(function (employee_data) {
                self.employees.forEach(function (employee) {
                    var data = _.findWhere(employee_data, {'id': employee.id});
                    if (data !== undefined){
                        employee.barcode = data.barcode;
                        employee.pin = data.pin;
                    }
                });
            });
        });
    },
    set_cashier: function(employee) {
        posmodel_super.set_cashier.apply(this, arguments);
        const selectedOrder = this.get_order();
        if (selectedOrder && !selectedOrder.get_orderlines().length) {
            // Order without lines can be considered to be un-owned by any employee.
            // We set the employee on that order to the currently set employee.
            selectedOrder.employee = employee;
        }
    }
});

var super_order_model = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function (attributes, options) {
        super_order_model.initialize.apply(this, arguments);
        if (!options.json) {
            this.employee = this.pos.get_cashier();
        }
    },
    init_from_JSON: function (json) {
        super_order_model.init_from_JSON.apply(this, arguments);
        if (this.pos.config.module_pos_hr && json.employee_id) {
            this.employee = this.pos.employee_by_id[json.employee_id];
        }
    },
    export_as_JSON: function () {
        const json = super_order_model.export_as_JSON.apply(this, arguments);
        if (this.pos.config.module_pos_hr) {
            json.employee_id = this.employee ? this.employee.id : false;
        }
        return json;
    },
});
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

});
