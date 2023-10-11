odoo.define('bi_pos_create_purchase_order.CustomErrorPopup', function(require) {
	'use strict';

	const ErrorPopup = require('point_of_sale.ErrorPopup');
	const Registries = require('point_of_sale.Registries');

	class CustomErrorPopup extends ErrorPopup {
		go_back_screen() {
			this.showScreen('ProductScreen');
			this.trigger('close-popup');
		}
	}
	CustomErrorPopup.template = 'CustomErrorPopup';
	CustomErrorPopup.defaultProps = {
		// confirmText: 'Ok',
		// cancelText: 'Cancel',
		title: 'Empty Order',
		body: 'There must be at least one product in your order before Add a note.',
	};

	Registries.Component.add(CustomErrorPopup);

	return CustomErrorPopup;
});
