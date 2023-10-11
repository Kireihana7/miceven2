/** @odoo-module **/

<<<<<<< HEAD
import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class ChatWindowHeader extends Component {
=======
const components = {
    ThreadIcon: require('mail/static/src/components/thread_icon/thread_icon.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');

const { Component } = owl;

class ChatWindowHeader extends Component {

    /**
     * @override
     */
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const chatWindow = this.env.models['mail.chat_window'].get(props.chatWindowLocalId);
            const thread = chatWindow && chatWindow.thread;
            return {
                chatWindow,
                chatWindowHasShiftLeft: chatWindow && chatWindow.hasShiftLeft,
                chatWindowHasShiftRight: chatWindow && chatWindow.hasShiftRight,
                chatWindowName: chatWindow && chatWindow.name,
                isDeviceMobile: this.env.messaging.device.isMobile,
                thread,
                threadLocalMessageUnreadCounter: thread && thread.localMessageUnreadCounter,
                threadMassMailing: thread && thread.mass_mailing,
                threadModel: thread && thread.model,
            };
        });
    }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {ChatWindow}
     */
    get chatWindow() {
        return this.props.chatWindow;
    }

    /**
     * @returns {ChatWindowHeaderView}
     */
<<<<<<< HEAD
     get chatWindowHeaderView() {
        return this.props.record;
=======
    _onClickClose(ev) {
        ev.stopPropagation();
        if (!this.chatWindow) {
            return;
        }
        this.chatWindow.close();
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickExpand(ev) {
        ev.stopPropagation();
        this.chatWindow.expand();
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickShiftLeft(ev) {
        ev.stopPropagation();
        if (this.props.saveThreadScrollTop) {
            this.props.saveThreadScrollTop();
        }
        this.chatWindow.shiftLeft();
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickShiftRight(ev) {
        ev.stopPropagation();
        if (this.props.saveThreadScrollTop) {
            this.props.saveThreadScrollTop();
        }
        this.chatWindow.shiftRight();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(ChatWindowHeader, {
    props: {
<<<<<<< HEAD
        chatWindow: Object,
        record: Object,
=======
        chatWindowLocalId: String,
        hasCloseAsBackButton: Boolean,
        isExpandable: Boolean,
        saveThreadScrollTop: {
            type: Function,
            optional: true,
        },
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    template: 'mail.ChatWindowHeader',
});

registerMessagingComponent(ChatWindowHeader);
