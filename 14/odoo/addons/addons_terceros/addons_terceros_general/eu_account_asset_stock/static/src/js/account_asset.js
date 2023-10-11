odoo.define('eu_account_asset_stock.StockRenderer', function(require) {
    "use strict";
    const AssetView = require('account_asset.AssetFormView');
    var core = require('web.core');
    var _t = core._t;
    var {Renderer} = AssetView.prototype.config;
    
    Renderer.include({
        _onAddOriginalStockMove: function(ev) {
            _.find(this.allFieldWidgets[this.state.id], x => x['name'] == 'original_stock_move_ids').onAddRecordOpenDialog();
        },
        events: Object.assign({}, Renderer.prototype.events, {
            'click .add_original_stock_move': '_onAddOriginalStockMove',
        }),
        /*
        * Open the m2o item selection from another button
        */
    });
});


    