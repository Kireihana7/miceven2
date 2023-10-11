/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');

const { Component } = owl;

<<<<<<< HEAD
export class MobileMessagingNavbar extends Component {
=======
class MobileMessagingNavbar extends Component {

    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps({
            compareDepth: {
                tabs: 2,
            },
        });
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    /**
     * @returns {MobileMessagingNavbarView}
     */
    get mobileMessagingNavbarView() {
        return this.props.record;
    }

}

Object.assign(MobileMessagingNavbar, {
    props: { record: Object },
    template: 'mail.MobileMessagingNavbar',
});

registerMessagingComponent(MobileMessagingNavbar);
