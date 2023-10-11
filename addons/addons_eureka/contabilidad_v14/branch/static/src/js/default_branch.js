odoo.define('branch.SwitchBranchMenu', function (require) {
    "use strict";
    /**
     * When Odoo is configured in multi-company mode, users should obviously be able
     * to switch their interface from one company to the other.  This is the purpose
     * of this widget, by displaying a dropdown menu in the systray.
     */

    var config = require('web.config');
    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var utils = require('web.utils');
    var request
    var _t = core._t;

    var SwitchBranchMenu = Widget.extend({
        template: 'SwitchBranchMenu',
        events: {
            'click .dropdown-item1[data-menu]': '_onSwitchBranchClick',
            'keydown .dropdown-item1[data-menu]': '_onSwitchBranchClick',
            // 'click .dropdown-item1[data-menu] div.toggle_branch': '_onToggleBranchClick',
            // 'keydown .dropdown-item1[data-menu] div.toggle_branch': '_onToggleBranchClick',
        },
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.isMobile = config.device.isMobile;
            this._onSwitchBranchClick = _.debounce(this._onSwitchBranchClick, 1500, true);
        },

        /**
         * @override
         */
        willStart: function () {
            var self = this;
            debugger;
            this.active_companies = session.user_context.allowed_company_ids || session.company_id;
            this.allowed_branch_ids = session
                .allowed_branch_ids
                .filter(branch => this.active_companies.includes(branch[1]))
                .map(i => i[0]);

            this.user_branches = session
                .user_branches
                .allowed_branch
                .filter(branch => this.active_companies.includes(branch[2]))
                .map(i => [i[0], i[1]]);

            var current_branchfiltered = session.branch_id;

            if (this.allowed_branch_ids.find(xbranch_id => xbranch_id == current_branchfiltered)) {
                this.current_branch = Number(current_branchfiltered);
            }
            else {
                this.current_branch = Number(this.allowed_branch_ids[0]);
                ajax.jsonRpc('/set_brnach', 'call', {
                    'BranchID': this.current_branch,
                }).then(() => {
                    session.setBranchB(this.current_branch, this.allowed_branch_ids);
                    // session.setBranch(this.current_branch, this.allowed_branch_ids);
// se hizo de esta manera para evitar que la pagina recargara dos veces con cambio de compañia,
// de momento no ha habido error, no obstante estamos inseguros si el setear directamente la variable de session no traera complicaciones futuras
                    odoo.session_info.branch_id=this.current_branch
                });
            }
            if (_.find(session.user_branches.allowed_branch.filter(branch => this.active_companies.includes(branch[2])), function (branch) {

                return branch[0] == self.current_branch;
            })) {
                this.current_branch_name = _.find(session.user_branches.allowed_branch.filter(branch => this.active_companies.includes(branch[2])), function (branch) {
                    return branch[0] == self.current_branch;
                })[1];


            }

            else {
                if (session.user_branches.allowed_branch.filter(branch => this.active_companies.includes(branch[2])).length) {

                    this.current_branch_name = session.user_branches.allowed_branch.filter(branch => this.active_companies.includes(branch[2]))[0][1]

                }
            }
            // ajax.jsonRpc('/set_brnach', 'call', {
            //     'BranchID': self.current_branch,
            // }).then(() => {
            //     session.setBranchB(self.current_branch, this.allowed_branch_ids);
            // });
            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {MouseEvent|KeyEvent} ev
         */
        _onSwitchBranchClick: function (ev) {
            if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
                return;
            }
            ev.preventDefault();
            ev.stopPropagation();
            var dropdownItem = $(ev.currentTarget);
            var dropdownMenu = dropdownItem;
            var branchID = dropdownItem.data('branch-id');
            var allowed_branch_ids = this.allowed_branch_ids;
            if (dropdownItem.find('.fa-square-o').length) {
                // 1 enabled company: Stay in single company mode
                if (this.allowed_branch_ids.length === 1) {
                    if (this.isMobile) {
                        dropdownMenu = dropdownMenu.parent();
                    }
                    dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                    dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                    allowed_branch_ids = [branchID];
                } else { // Multi company mode
                    allowed_branch_ids.push(branchID);
                    dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                }
            }
            $(ev.currentTarget).attr('aria-pressed', 'true');
            // ajax.jsonRpc('/set_brnach', 'call', {
            //     'BranchID':  branchID,
            // })
            ajax.jsonRpc('/set_brnach', 'call', {
                'BranchID': branchID,
            }).then(() => {
                session.setBranch(branchID, allowed_branch_ids);
            });
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {MouseEvent|KeyEvent} ev
         */
        _onToggleBranchClick: function (ev) {
            if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
                return;
            }
            ev.preventDefault();
            ev.stopPropagation();
            var dropdownItem = $(ev.currentTarget).parent();
            var branchID = dropdownItem.data('branch-id');
            var allowed_branch_ids = this.allowed_branch_ids;
            var current_branch_id = Number(allowed_branch_ids[0]);
            if (dropdownItem.find('.fa-square-o').length) {
                allowed_branch_ids.push(branchID);
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                $(ev.currentTarget).attr('aria-checked', 'true');
            } else {
                allowed_branch_ids.splice(allowed_branch_ids.indexOf(branchID), 1);
                dropdownItem.find('.fa-check-square').addClass('fa-square-o').removeClass('fa-check-square');
                $(ev.currentTarget).attr('aria-checked', 'false');
            }
            session.setBranch(current_branch_id, allowed_branch_ids);
        },

    });

    if (session.display_switch_branch_menu) {
        SystrayMenu.Items.push(SwitchBranchMenu);
    }

    return SwitchBranchMenu;

});