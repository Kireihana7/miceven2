odoo.define('quick_access_currency_rate.SystrayItem', function (require) {
"use strict";

var Widget = require('web.Widget');
var SystrayMenu = require('web.SystrayMenu');
var core = require('web.core');
var QWeb = core.qweb;
var Session = require('web.session');
var _t = core._t;

var QuickAccessCurencyRate = Widget.extend({
    template:'quick_access_currency_rate.systray_item',
    events: {
        'show.bs.dropdown': '_onShowDropdown',
    },
    willStart: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            return Session.user_has_group('account.group_account_invoice').then(function (has_group) {
                self.group_account_invoice = has_group;
            });
        });
    },    
    /**
     * @override
     */
    start: function () {
        this._$previews = this.$('.o_currency_rate_systray_dropdown_items');
        this._currencies = [];
        return this._super.apply(this, arguments);
    },
    _saveCurrencies: function(ev){
        var updateCurrencies = {};
        _.each(this._currencies, function(cur){
            var xmlId = '#quick-currency-' + cur.id;
            var $input = $(xmlId);
            if ($input && $input.val()){
                var rate = parseFloat($input.val());
                if (cur.rate !== rate){
                    updateCurrencies[cur.id] = rate;
                }
            }
        });
        if (updateCurrencies){
            return this._rpc({
                model: 'res.currency',
                method: 'service_set_currency_rates',
                args: [updateCurrencies],
            });
        }
    },
    _openCurrencies: function(ev){
        this.do_action({
            type: 'ir.actions.act_window',
            res_model: 'res.currency',
            views: [[false, 'list'], [false, 'form']],
            name: _t('Currencies'),
        });
    },
    /**
     * @private
     * @param  {MouseEvent} ev
     */
    _onShowDropdown: function () {
        this._updatePreviews();
    },
    _getCurrencies: function () {
        return this._rpc({
            model: 'res.currency',
            method: 'service_get_currencies',
        });
    },    
    _renderPreviews: function (previews) {
        var $currency = {}
        var self = this;
        _.each(previews, function(rec){
            if (rec.rate === 1){
                $currency = rec;
                return;
            }
        });
        if (previews){
            previews.splice(previews.indexOf($currency), 1 );
        }
        this._currencies = previews;
        this._$previews.html(QWeb.render('quick_access_currency_rate.main_view', {
            previews: previews,
            base_currency: $currency,
        }));
        $('.o_currency_rate_systray_dropdown_item').on('click', function (ev) {
            ev.stopPropagation();
        });
        $('.btn-open-currency').on('click', function (ev) {
            self._openCurrencies(ev);
        });
        $('.btn-save-currency').on('click', function (ev) {
            self._saveCurrencies(ev);
        });
    },
    _updatePreviews: function () {
        // Display spinner while waiting for conversations preview
        this._$previews.html(QWeb.render('Spinner'));
        this._getCurrencies()
            .then(this._renderPreviews.bind(this));
    },
});

SystrayMenu.Items.push(QuickAccessCurencyRate);

return QuickAccessCurencyRate;

});