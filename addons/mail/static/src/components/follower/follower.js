/** @odoo-module **/

<<<<<<< HEAD
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    FollowerSubtypeList: require('mail/static/src/components/follower_subtype_list/follower_subtype_list.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { markEventHandled } = require('mail/static/src/utils/utils.js');
const { Component } = owl;

export class Follower extends Component {
    /**
     * @returns {FollowerView}
     */
<<<<<<< HEAD
    get followerView() {
        return this.props.record;
    }
=======
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const follower = this.env.models['mail.follower'].get(props.followerLocalId);
            return [follower ? follower.__state : undefined];
        });
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {mail.follower}
     */
    get follower() {
        return this.env.models['mail.follower'].get(this.props.followerLocalId);
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickDetails(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this.follower.openProfile();
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickEdit(ev) {
        ev.preventDefault();
        this.follower.showSubtypes();
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    async _onClickRemove(ev) {
        markEventHandled(ev, 'Follower.clickRemove');
        await this.follower.remove();
        this.trigger('reload', { fieldNames:['message_follower_ids'], keepChanges: true });
        this.trigger('o-hide-follower-list-menu');
    }

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
}

Object.assign(Follower, {
    props: { record: Object },
    template: 'mail.Follower',
});

registerMessagingComponent(Follower);
