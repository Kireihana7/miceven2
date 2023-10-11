/** @odoo-module **/

<<<<<<< HEAD
import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class ChatWindowManager extends Component {}
=======
const components = {
    ChatWindow: require('mail/static/src/components/chat_window/chat_window.js'),
    ChatWindowHiddenMenu: require('mail/static/src/components/chat_window_hidden_menu/chat_window_hidden_menu.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');

const { Component } = owl;

class ChatWindowManager extends Component {

    /**
     * @override
     */
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const chatWindowManager = this.env.messaging && this.env.messaging.chatWindowManager;
            const allOrderedVisible = chatWindowManager
                ? chatWindowManager.allOrderedVisible
                : [];
            return {
                allOrderedVisible,
                allOrderedVisibleThread: allOrderedVisible.map(chatWindow => chatWindow.thread),
                chatWindowManager,
                chatWindowManagerHasHiddenChatWindows: chatWindowManager && chatWindowManager.hasHiddenChatWindows,
                isMessagingInitialized: this.env.isMessagingInitialized(),
            };
        }, {
            compareDepth: {
                allOrderedVisible: 1,
                allOrderedVisibleThread: 1,
            },
        });
    }

}
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

Object.assign(ChatWindowManager, {
    props: { record: Object },
    template: 'mail.ChatWindowManager',
});

registerMessagingComponent(ChatWindowManager);
