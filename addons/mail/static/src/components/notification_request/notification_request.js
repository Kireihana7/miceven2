<<<<<<< HEAD
/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class NotificationRequest extends Component {
=======
odoo.define('mail/static/src/components/notification_request/notification_request.js', function (require) {
'use strict';

const components = {
    PartnerImStatusIcon: require('mail/static/src/components/partner_im_status_icon/partner_im_status_icon.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');

const { Component } = owl;

class NotificationRequest extends Component {

    /**
     * @override
     */
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            return {
                isDeviceMobile: this.env.messaging.device.isMobile,
                partnerRoot: this.env.messaging.partnerRoot
                    ? this.env.messaging.partnerRoot.__state
                    : undefined,
            };
        });
    }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
<<<<<<< HEAD
     * @returns {NotificationRequestView}
     */
    get notificationRequestView() {
        return this.props.record;
=======
     * @returns {string}
     */
    getHeaderText() {
        return _.str.sprintf(
            this.env._t("%s has a request"),
            this.env.messaging.partnerRoot.nameOrDisplayName
        );
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Handle the response of the user when prompted whether push notifications
     * are granted or denied.
     *
     * @private
     * @param {string} value
     */
    _handleResponseNotificationPermission(value) {
<<<<<<< HEAD
        this.messaging.refreshIsNotificationPermissionDefault();
        if (value !== 'granted') {
            this.messaging.userNotificationManager.sendNotification({
                message: this.env._t("Odoo will not have the permission to send native notifications on this device."),
                title: this.env._t("Permission denied"),
            });
=======
        // manually force recompute because the permission is not in the store
        this.env.messaging.messagingMenu.update();
        if (value !== 'granted') {
            this.env.services['bus_service'].sendNotification(
                this.env._t("Permission denied"),
                this.env._t("Odoo will not have the permission to send native notifications on this device.")
            );
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClick() {
<<<<<<< HEAD
        const windowNotification = this.messaging.browser.Notification;
=======
        const windowNotification = this.env.browser.Notification;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        const def = windowNotification && windowNotification.requestPermission();
        if (def) {
            def.then(this._handleResponseNotificationPermission.bind(this));
        }
<<<<<<< HEAD
        if (!this.messaging.device.isSmall) {
            this.messaging.messagingMenu.close();
=======
        if (!this.env.messaging.device.isMobile) {
            this.env.messaging.messagingMenu.close();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
    }

}

Object.assign(NotificationRequest, {
<<<<<<< HEAD
    props: { record: Object },
    template: 'mail.NotificationRequest',
});

registerMessagingComponent(NotificationRequest);
=======
    components,
    props: {},
    template: 'mail.NotificationRequest',
});

return NotificationRequest;

});
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
