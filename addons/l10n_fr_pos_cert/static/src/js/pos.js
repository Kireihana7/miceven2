odoo.define('l10n_fr_pos_cert.pos', function (require) {
"use strict";

const { Gui } = require('point_of_sale.Gui');
var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
var core = require('web.core');
const Registries = require('point_of_sale.Registries');

var _t = core._t;

const L10nFrPosGlobalState = (PosGlobalState) => class L10nFrPosGlobalState extends PosGlobalState {
    is_french_country(){
      var french_countries = ['FR', 'MF', 'MQ', 'NC', 'PF', 'RE', 'GF', 'GP', 'TF'];
      if (!this.company.country) {
        Gui.showPopup("ErrorPopup", {
            'title': _t("Missing Country"),
            'body':  _.str.sprintf(_t('The company %s doesn\'t have a country set.'), this.company.name),
        });
        return false;
      }
      return _.contains(french_countries, this.company.country.code);
    }
    disallowLineQuantityChange() {
        let result = super.disallowLineQuantityChange(...arguments);
        let selectedOrderLine = this.selectedOrder.get_selected_orderline();
        //Note: is_reward_line is a field in the pos_loyalty module
        if (selectedOrderLine.is_reward_line) {
            //Always allow quantity change for reward lines
            return false || result;
        }
        return this.is_french_country() || result;
    }
}
Registries.Model.extend(PosGlobalState, L10nFrPosGlobalState);


const L10nFrOrder = (Order) => class L10nFrOrder extends Order {
    constructor() {
        super(...arguments);
        this.l10n_fr_hash = this.l10n_fr_hash || false;
        this.save_to_db();
    }
    export_for_printing() {
      var result = super.export_for_printing(...arguments);
      result.l10n_fr_hash = this.get_l10n_fr_hash();
      return result;
    }
    set_l10n_fr_hash (l10n_fr_hash){
      this.l10n_fr_hash = l10n_fr_hash;
    }
    get_l10n_fr_hash() {
      return this.l10n_fr_hash;
    }
    wait_for_push_order() {
      var result = super.wait_for_push_order(...arguments);
      result = Boolean(result || this.pos.is_french_country());
      return result;
    }
    destroy (option) {
        // SUGGESTION: It's probably more appropriate to apply this restriction
        // in the TicketScreen.
        if (option && option.reason == 'abandon' && this.pos.is_french_country() && this.get_orderlines().length) {
            Gui.showPopup("ErrorPopup", {
                'title': _t("Fiscal Data Module error"),
                'body':  _t("Deleting of orders is not allowed."),
            });
        } else {
<<<<<<< HEAD
            super.destroy(...arguments);
=======
            _super_posmodel.delete_current_order.apply(this, arguments);
        }
    },

    disallowLineQuantityChange() {
        let result = _super_posmodel.disallowLineQuantityChange.bind(this)();
        return this.is_french_country() || result;
    }
});


var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function() {
        _super_order.initialize.apply(this,arguments);
        this.l10n_fr_hash = this.l10n_fr_hash || false;
        this.save_to_db();
    },
    export_for_printing: function() {
      var result = _super_order.export_for_printing.apply(this,arguments);
      result.l10n_fr_hash = this.get_l10n_fr_hash();
      return result;
    },
    set_l10n_fr_hash: function (l10n_fr_hash){
      this.l10n_fr_hash = l10n_fr_hash;
    },
    get_l10n_fr_hash: function() {
      return this.l10n_fr_hash;
    },
    wait_for_push_order: function() {
      var result = _super_order.wait_for_push_order.apply(this,arguments);
      result = Boolean(result || this.pos.is_french_country());
      return result;
    }
});

var orderline_super = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    can_be_merged_with: function(orderline) {
        if (this.pos.is_french_country()) {
            const order = this.pos.get_order();
            const lastId = order.orderlines.last().cid;
            if ((order.orderlines._byId[lastId].product.id !== orderline.product.id || order.orderlines._byId[lastId].quantity < 0)) {
                return false;
            }
            return orderline_super.can_be_merged_with.apply(this, arguments);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        return orderline_super.can_be_merged_with.apply(this, arguments);
    }
}
Registries.Model.extend(Order, L10nFrOrder);


const L10nFrOrderline = (Orderline) => class L10nFrOrderline extends Orderline {
    can_be_merged_with(orderline) {
        if (this.pos.is_french_country()) {
            const order = this.pos.get_order();
            const lastOrderline = order.orderlines.at(order.orderlines.length - 1);
            if ((lastOrderline.product.id !== orderline.product.id || lastOrderline.quantity < 0)) {
                return false;
            }
            return super.can_be_merged_with(...arguments);
        }
        return super.can_be_merged_with(...arguments);
    }
}
Registries.Model.extend(Orderline, L10nFrOrderline);

});
