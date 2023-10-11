<<<<<<< HEAD
/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
odoo.define('website_livechat/static/src/components/visitor_banner/visitor_banner.js', function (require) {
'use strict';

const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

class VisitorBanner extends Component {

<<<<<<< HEAD
=======
    /**
     * @override
     */
    constructor(...args) {
        super(...args);
        useStore(props => {
            const visitor = this.env.models['website_livechat.visitor'].get(props.visitorLocalId);
            const country = visitor && visitor.country;
            return {
                country: country && country.__state,
                visitor: visitor ? visitor.__state : undefined,
            };
        });
    }

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
<<<<<<< HEAD
     * @returns {Visitor}
     */
    get visitor() {
        return this.props.visitor;
=======
     * @returns {website_livechat.visitor}
     */
    get visitor() {
        return this.env.models['website_livechat.visitor'].get(this.props.visitorLocalId);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(VisitorBanner, {
<<<<<<< HEAD
    props: { visitor: Object },
    template: 'website_livechat.VisitorBanner',
});

registerMessagingComponent(VisitorBanner);

export default VisitorBanner;
=======
    props: {
        visitorLocalId: String,
    },
    template: 'website_livechat.VisitorBanner',
});

return VisitorBanner;

});
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
