odoo.define("hr_attendance_geofence.user_menu", function (require) {
    "use strict";

    var UserMenu = require("web.UserMenu");
    var session = require("web.session");

    UserMenu.include({
        _onMenuGeolocation: function() {
            var self = this;
            this.trigger_up("clear_uncommitted_changes", {
                callback: function() {
                    self._rpc({
                        route: "/web/action/load", 
                        params: { 
                            action_id: "hr_attendance_geofence.action_simple_attendance_geolocation"
                        }
                    }).then(function(result) {
                        result.res_id = session.uid;
                        self.do_action(result);
                    });
                },
            });
        },
    });

});