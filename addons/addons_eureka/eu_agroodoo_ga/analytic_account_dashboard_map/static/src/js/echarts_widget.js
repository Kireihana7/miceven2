odoo.define('widget_echart', function(require) {
'use strict'

    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');

    var EChartWidget = AbstractField.extend({
        _renderReadonly: function() {
            var val = this.value;
            this.$el.html(val);
        }
    });
    fieldRegistry.add('echart', EChartWidget);
    return {
        EChartWidget: EChartWidget
    };
});