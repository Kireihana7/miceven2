/** @odoo-module **/

<<<<<<< HEAD
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

export class MessageAuthorPrefix extends Component {

    /**
     * @returns {MessageAuthorPrefixView}
     */
<<<<<<< HEAD
    get messageAuthorPrefixView() {
        return this.props.record;
=======
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const message = this.env.models['mail.message'].get(props.messageLocalId);
            const author = message ? message.author : undefined;
            const thread = props.threadLocalId
                ? this.env.models['mail.thread'].get(props.threadLocalId)
                : undefined;
            return {
                author: author ? author.__state : undefined,
                currentPartner: this.env.messaging.currentPartner
                    ? this.env.messaging.currentPartner.__state
                    : undefined,
                message: message ? message.__state : undefined,
                thread: thread ? thread.__state : undefined,
            };
        });
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {mail.message}
     */
    get message() {
        return this.env.models['mail.message'].get(this.props.messageLocalId);
    }

    /**
     * @returns {mail.thread|undefined}
     */
    get thread() {
        return this.env.models['mail.thread'].get(this.props.threadLocalId);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(MessageAuthorPrefix, {
    props: { record: Object },
    template: 'mail.MessageAuthorPrefix',
});

registerMessagingComponent(MessageAuthorPrefix);
