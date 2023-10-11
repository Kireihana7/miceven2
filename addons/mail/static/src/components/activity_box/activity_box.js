/** @odoo-module **/

<<<<<<< HEAD
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    Activity: require('mail/static/src/components/activity/activity.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

export class ActivityBox extends Component {

    /**
     * @returns {ActivityBoxView}
     */
<<<<<<< HEAD
    get activityBoxView() {
        return this.props.record;
=======
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const chatter = this.env.models['mail.chatter'].get(props.chatterLocalId);
            const thread = chatter && chatter.thread;
            return {
                chatter: chatter ? chatter.__state : undefined,
                thread: thread && thread.__state,
            };
        });
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {Chatter}
     */
    get chatter() {
        return this.env.models['mail.chatter'].get(this.props.chatterLocalId);
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClickTitle(ev) {
        ev.preventDefault();
        this.chatter.toggleActivityBoxVisibility();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(ActivityBox, {
    props: { record: Object },
    template: 'mail.ActivityBox',
});

registerMessagingComponent(ActivityBox);
