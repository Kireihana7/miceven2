/** @odoo-module **/
odoo.define("eu_shipping_record.TripDashboard", function(require) {
    "use strict";
    
    const core = require('web.core');
    const ListRenderer = require('web.ListRenderer');
    const ListView = require('web.ListView');
    const view_registry = require('web.view_registry');
    const { qweb: QWeb } = core;

    const Renderer = ListRenderer.extend({
        events: _.extend({}, ListRenderer.prototype.events, {
            'click .trip-kpi': 'onClickKpi',
        }),
        _renderView() {
            return this._super.apply(this, arguments).then(async() => {
                const STATES = [
                    "planificado",
                    "en_proceso",
                    "finalizado",
                    "facturado",
                ];

                const CAN_INVOICE = await this._rpc({
                    model: "fleet.trip",
                    method: "action_get_parameter",
                    args: [[]],
                });

                if(!CAN_INVOICE) STATES.pop();

                let count = await this._rpc({
                    model: "fleet.trip",
                    method: 'search_read',
                    kwargs: {
                        domain: [],
                        fields: ['state'],
                    },
                });

                count = Object.fromEntries(
                    STATES.map((status) => [status, count.filter(({ state }) => state === status).length])
                );

                const $dashboard = QWeb.render('eu_shipping_record.TripDashboard', {
                    count,
                    records: this.state.data,
                    states: STATES,
                });

                this.$el.prepend($dashboard);
            });
        },
        onClickKpi(e) {
            const { currentTarget: $target } = e;

            if(Number($target.querySelector("span[name='trip-counter']").textContent) === 0) {
                return alert("No hay viajes en ese estatus");
            }

            return this.do_action({
                type: 'ir.actions.act_window',
                name: this.arch.attrs.string,
                res_model: this.state.model,
                views: [
                    [false, "tree"],
                    [false, "form"],
                    [false, "search"],
                ],
                domain: [
                    ["state", "=", $target.dataset.tripState]
                ],
                target: "current",
            });
        }
    });
    
    const tripDashboard = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Renderer,
        }),
    });
    
    view_registry.add('trip-dashboard', tripDashboard);
    
    return { Renderer };
});