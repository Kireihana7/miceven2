/** @odoo-module **/
odoo.define("eu_sales_visit.VisitDashboard", function(require) {
    "use strict";
    
    const core = require('web.core');
    const ListRenderer = require('web.ListRenderer');
    const ListView = require('web.ListView');
    const view_registry = require('web.view_registry');
    const { qweb: QWeb } = core;

    const Renderer = ListRenderer.extend({
        events: _.extend({}, ListRenderer.prototype.events, {
            'click .visit-kpi': 'onClickKpi',
        }),
        _renderView() {
            return this._super.apply(this, arguments).then(async() => {
                console.time("Visits");

                const visits = await this._rpc({
                    model: "res.visit",
                    method: 'search_read',
                    kwargs: {
                        domain: [],
                        fields: ['status'],
                    },
                });

                console.info(`Fetched ${visits.length} visits`);
                console.timeEnd("Visits");

                const count = {};
                
                visits.forEach(({ status }) => {
                    if(!(status in count)) {
                        count[status] = 1;
                    } else {
                        count[status]++;
                    }
                });

                let states = [
                    "por_visitar",
                    "no_visitado",
                    "visitando",
                    "efectiva",
                    "no_efectiva",
                ];

                states = states.map((state) => [state, ("/eu_sales_visit/static/src/img/" + state + ".png")])
                states = Object.fromEntries(states);

                const $dashboard = QWeb.render('eu_sales_visit.VisitDashboard', {
                    count,
                    records: this.state.data,
                    states,
                });

                this.$el.prepend($dashboard);
            });
        },
        onClickKpi(e) {
            const { currentTarget: $target } = e;

            if(Number($target.querySelector("span[name='visit-counter']").textContent) === 0) {
                return alert("No hay visitas en ese estatus");
            }

            return this.do_action({
                type: 'ir.actions.act_window',
                name: this.arch.attrs.string,
                res_model: this.state.model,
                views: [
                    [false, "tree"],
                    [false, "form"],
                    [false, "calendar"],
                    [false, "pivot"],
                    [false, "graph"],
                ],
                domain: [
                    //...this.state.domain, 
                    ["status", "=", $target.dataset.visitState]
                ],
                target: "current",
            });
        }
    });
    
    const VisitDashboard = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Renderer,
        }),
    });
    
    view_registry.add('visit-dashboard', VisitDashboard);
    
    return { Renderer };
});