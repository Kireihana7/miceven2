odoo.define('eu_agrodinstry.chargue_consolidate', function (require) {
    "use strict";
    
    
    /**
     * This file defines the Agro Dashboard view (alongside its renderer, model
     * and controller). This Dashboard is added to the top of list Agro
     * views, it extends both views with essentially the same code except for
     * _onDashboardActionClicked function so we can apply filters without changing our
     * current view.
     */
    
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListModel = require('web.ListModel');
    var ListRenderer = require('web.ListRenderer');
    var ListView = require('web.ListView');
    var SampleServer = require('web.SampleServer');
    var view_registry = require('web.view_registry');
    
    var QWeb = core.qweb;
    
    // Add mock of method 'retrieve_quotes' in SampleServer, so that we can have
    // the sample data in empty Agro list view
    let dashboardValues;
    SampleServer.mockRegistry.add('chargue.consolidate/retrieve_quotes', () => {
        return Object.assign({}, dashboardValues);
    });
    
    
    //--------------------------------------------------------------------------
    // List View
    //--------------------------------------------------------------------------
    
    var AgroListDashboardRenderer = ListRenderer.extend({
        events:_.extend({}, ListRenderer.prototype.events, {
            'click .o_dashboard_action': '_onDashboardActionClicked',
        }),
        /**
         * @override
         * @private
         * @returns {Promise}
         */
        _renderView: function () {
            var self = this;
            
            return this._super.apply(this, arguments).then(async () => {
                const usar_patio = await this._rpc({
                    model: "chargue.consolidate",
                    method: "can_usar_patio",
                });
    
                var values = self.state.dashboardValues;
                var agro = QWeb.render('eu_agroindustry.AgroDashboard', { values, usar_patio });
                self.$el.prepend(agro);
            });
        },
    
        /**
         * @private
         * @param {MouseEvent}
         */
        _onDashboardActionClicked: function (e) {
            e.preventDefault();
            var $action = $(e.currentTarget);
            this.trigger_up('dashboard_open_action', {
                action_name: $action.attr('name'),
                action_context: $action.attr('context'),
            });
        },
    });
    
    var AgroListDashboardModel = ListModel.extend({
        /**
         * @override
         */
        init: function () {
            this.dashboardValues = {};
            this._super.apply(this, arguments);
        },
    
        /**
         * @override
         */
        __get: function (localID) {
            var result = this._super.apply(this, arguments);
            if (_.isObject(result)) {
                result.dashboardValues = this.dashboardValues[localID];
            }
            return result;
        },
        /**
         * @override
         * @returns {Promise}
         */
        __load: function () {
            return this._loadDashboard(this._super.apply(this, arguments));
        },
        /**
         * @override
         * @returns {Promise}
         */
        __reload: function () {
            return this._loadDashboard(this._super.apply(this, arguments));
        },
    
        /**
         * @private
         * @param {Promise} super_def a promise that resolves with a dataPoint id
         * @returns {Promise -> string} resolves to the dataPoint id
         */
        _loadDashboard: function (super_def) {
            var self = this;
            var dashboard_def = this._rpc({
                model: 'chargue.consolidate',
                method: 'retrieve_quotes',
            });
            return Promise.all([super_def, dashboard_def]).then(function(results) {
                var id = results[0];
                dashboardValues = results[1];
                self.dashboardValues[id] = dashboardValues;
                return id;
            });
        },
    });
    
    var AgroListDashboardController = ListController.extend({
        custom_events: _.extend({}, ListController.prototype.custom_events, {
            dashboard_open_action: '_onDashboardOpenAction',
        }),
    
        /**
         * @private
         * @param {OdooEvent} e
         */

        _onDashboardOpenAction: function (e) {
            var self = this;
            var action_name = e.data.action_name;
            if (_.contains(['agros_por_llegar','agros_patio','agros_peso_bruto',
                'agros_proceso','agros_peso_tara','agros_por_salir','agros_finalizado'], action_name)) {
                return this._rpc({model: this.modelName, method: action_name})
                    .then(function (data) {
                        if (data) {
                        return self.do_action(data);
                        }
                    });
            }
            return this.do_action(action_name);
        },
    });
    
    var AgroListDashboardView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Model: AgroListDashboardModel,
            Renderer: AgroListDashboardRenderer,
            Controller: AgroListDashboardController,
        }),
    });
    
    view_registry.add('agro_list_dashboard', AgroListDashboardView);
    
    return {
        AgroListDashboardModel: AgroListDashboardModel,
        AgroListDashboardRenderer: AgroListDashboardRenderer,
        AgroListDashboardController: AgroListDashboardController,
    };
    
    });