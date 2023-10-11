/** @odoo-module **/

<<<<<<< HEAD
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    ThreadTypingIcon: require('mail/static/src/components/thread_typing_icon/thread_typing_icon.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

export class ThreadIcon extends Component {

    /**
<<<<<<< HEAD
     * @returns {Thread}
=======
     * @override
     */
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const thread = this.env.models['mail.thread'].get(props.threadLocalId);
            const correspondent = thread ? thread.correspondent : undefined;
            return {
                correspondent,
                correspondentImStatus: correspondent && correspondent.im_status,
                history: this.env.messaging.history,
                inbox: this.env.messaging.inbox,
                moderation: this.env.messaging.moderation,
                partnerRoot: this.env.messaging.partnerRoot,
                starred: this.env.messaging.starred,
                thread,
                threadChannelType: thread && thread.channel_type,
                threadModel: thread && thread.model,
                threadOrderedOtherTypingMembersLength: thread && thread.orderedOtherTypingMembers.length,
                threadPublic: thread && thread.public,
                threadTypingStatusText: thread && thread.typingStatusText,
            };
        });
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {mail.thread}
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
     */
    get thread() {
        return this.props.thread;
    }

}

Object.assign(ThreadIcon, {
    props: { thread: Object },
    template: 'mail.ThreadIcon',
});

registerMessagingComponent(ThreadIcon);
