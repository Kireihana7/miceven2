/** @odoo-module **/

<<<<<<< HEAD
import { usePosition } from "@web/core/position_hook";
import { useRefToModel } from '@mail/component_hooks/use_ref_to_model';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    Follower: require('mail/static/src/components/follower/follower.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
const { isEventHandled } = require('mail/static/src/utils/utils.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component, useRef } = owl;

export class FollowerListMenu extends Component {

    /**
     * @override
     */
<<<<<<< HEAD
    setup() {
        super.setup();
        useRefToModel({ fieldName: 'dropdownRef', refName: 'dropdown' });
        this.togglerRef = useRef("toggler");
        usePosition(() => this.togglerRef.el, {
            position: "bottom-end",
        });
=======
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        this.state = useState({
            /**
             * Determine whether the dropdown is open or not.
             */
            isDropdownOpen: false,
        });
        useStore(props => {
            const thread = this.env.models['mail.thread'].get(props.threadLocalId);
            const followers = thread ? thread.followers : [];
            return {
                followers,
                threadChannelType: thread && thread.channel_type,
            };
        }, {
            compareDepth: {
                followers: 1,
            },
        });
        this._dropdownRef = useRef('dropdown');
        this._onClickCaptureGlobal = this._onClickCaptureGlobal.bind(this);
    }

    mounted() {
        document.addEventListener('click', this._onClickCaptureGlobal, true);
    }

    willUnmount() {
        document.removeEventListener('click', this._onClickCaptureGlobal, true);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @return {FollowerListMenuView}
     */
    get followerListMenuView() {
        return this.props.record;
    }

<<<<<<< HEAD
=======
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _hide() {
        this.state.isDropdownOpen = false;
    }

    /**
     * @private
     * @param {KeyboardEvent} ev
     */
    _onKeydown(ev) {
        ev.stopPropagation();
        switch (ev.key) {
            case 'Escape':
                ev.preventDefault();
                this._hide();
                break;
        }
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickAddChannels(ev) {
        ev.preventDefault();
        this._hide();
        this.thread.promptAddChannelFollower();
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickAddFollowers(ev) {
        ev.preventDefault();
        this._hide();
        this.thread.promptAddPartnerFollower();
    }

    /**
     * Close the dropdown when clicking outside of it.
     *
     * @private
     * @param {MouseEvent} ev
     */
    _onClickCaptureGlobal(ev) {
        // since dropdown is conditionally shown based on state, dropdownRef can be null
        if (this._dropdownRef.el && !this._dropdownRef.el.contains(ev.target)) {
            this._hide();
        }
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickFollowersButton(ev) {
        this.state.isDropdownOpen = !this.state.isDropdownOpen;
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickFollower(ev) {
        if (isEventHandled(ev, 'Follower.clickRemove')) {
            return;
        }
        this._hide();
    }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
}

Object.assign(FollowerListMenu, {
    props: { record: Object },
    template: 'mail.FollowerListMenu',
});

registerMessagingComponent(FollowerListMenu);
