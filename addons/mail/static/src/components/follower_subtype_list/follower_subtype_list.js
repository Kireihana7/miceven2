/** @odoo-module **/

<<<<<<< HEAD
import { useComponentToModel } from '@mail/component_hooks/use_component_to_model';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    FollowerSubtype: require('mail/static/src/components/follower_subtype/follower_subtype.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

export class FollowerSubtypeList extends Component {

    /**
     * @override
     */
<<<<<<< HEAD
     setup() {
        super.setup();
        useComponentToModel({ fieldName: 'component' });
=======
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const followerSubtypeList = this.env.models['mail.follower_subtype_list'].get(props.localId);
            const follower = followerSubtypeList
                ? followerSubtypeList.follower
                : undefined;
            const followerSubtypes = follower ? follower.subtypes : [];
            return {
                follower: follower ? follower.__state : undefined,
                followerSubtypeList: followerSubtypeList
                    ? followerSubtypeList.__state
                    : undefined,
                followerSubtypes: followerSubtypes.map(subtype => subtype.__state),
            };
        }, {
            compareDepth: {
                followerSubtypes: 1,
            },
        });
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {FollowerSubtypeList}
     */
    get followerSubtypeList() {
        return this.props.record;
    }

}

Object.assign(FollowerSubtypeList, {
    props: { record: Object },
    template: 'mail.FollowerSubtypeList',
});

registerMessagingComponent(FollowerSubtypeList);
