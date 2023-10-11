odoo.define('echart_odoo', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');


    var bargraph = AbstractAction.extend({
        // corresponds to t-name in xml
        template: 'echarts_bargraph_template',

        init: function(parent, data){
            return this._super.apply(this, arguments);
        },

        start: function(){
            this._setTitle('KPI');
            return true;
        },
    });
    core.action_registry.add('eu_echart_odoo.echart_odoo_bargraph', bargraph);
})

