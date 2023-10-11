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

export class ThreadTextualTypingStatus extends Component {

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
            return {
                threadOrderedOtherTypingMembersLength: thread && thread.orderedOtherTypingMembersLength,
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

Object.assign(ThreadTextualTypingStatus, {
    props: { thread: Object },
    template: 'mail.ThreadTextualTypingStatus',
});

registerMessagingComponent(ThreadTextualTypingStatus);
