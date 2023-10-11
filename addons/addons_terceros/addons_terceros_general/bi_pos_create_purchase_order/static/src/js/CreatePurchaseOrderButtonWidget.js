odoo.define('bi_pos_create_purchase_order.CreatePurchaseOrderButtonWidget', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	const ProductScreen = require('point_of_sale.ProductScreen');
	var core = require('web.core');
	const { Gui } = require('point_of_sale.Gui');
	const Popup = require('point_of_sale.ConfirmPopup');
	var field_utils = require('web.field_utils');
	var rpc = require('web.rpc');
	var session = require('web.session');
	var time = require('web.time');
	var utils = require('web.utils');
	const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
	var _t = core._t;

	// Start CreatePurchaseOrderButtonWidget
	class CreatePurchaseOrderButtonWidget extends PosComponent {
        constructor() {
            super(...arguments);
        }

		renderElement(){
			var self = this;
				
			var order = self.env.pos.get('selectedOrder');

			var partner_id = false
			if (order.get_client() != null)
				partner_id = order.get_client().id;
			
			 // Popup Occurs when no Customer is selected...
			if (!partner_id) {
				self.showPopup('noCustomerPopup', {});
				return;
			}

			var orderlines = order.orderlines;
			var cashier_id = self.env.pos.get_cashier().user_id[0];
			// Popup Occurs when not a single product in orderline...
				if (orderlines.length === 0) {
					self.showPopup('CustomErrorPopup', {});
					return;
				}
			var po_state = self.env.pos.config.po_state
			var pos_product_list = [];
			for (var i = 0; i < orderlines.length; i++) {
				var product_items = {
					'id': orderlines.models[i].product.id,
					'quantity': orderlines.models[i].quantity,
					'uom_id': orderlines.models[i].product.uom_id[0],
					'price': orderlines.models[i].price,
					'discount': orderlines.models[i].discount,
				};
				
				pos_product_list.push({'product': product_items });
			}
			this.rpc({
				model: 'purchase.order',
				method: 'create_purchase_order_ui',
				args: [partner_id, partner_id, pos_product_list, cashier_id,po_state,order.pos_session_id],
			
			}).then(function(output) {
				if(orderlines.length > 0){
					for (var line in orderlines)
					{
						order.remove_orderline(order.get_orderlines());
					}
				}
				order.set_client(false)
				alert('Creada la Orden de Compra');
				self.showScreen('ProductScreen');

			});
			// this.env.pos.delete_current_order();

		}
	};

	CreatePurchaseOrderButtonWidget.template = 'CreatePurchaseOrderButtonWidget';

    Registries.Component.add(CreatePurchaseOrderButtonWidget);

    return CreatePurchaseOrderButtonWidget;
	// End CreatePurchaseOrderButtonWidget	


});
