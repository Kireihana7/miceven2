/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');

const { Component } = owl;

<<<<<<< HEAD
export class AttachmentList extends Component {

    /**
     * @returns {AttachmentList}
     */
    get attachmentList() {
        return this.props.record;
=======
class AttachmentList extends Component {

    /**
     * @override
     */
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps({
            compareDepth: {
                attachmentLocalIds: 1,
            },
        });
        useStore(props => {
            const attachments = this.env.models['mail.attachment'].all().filter(attachment =>
                props.attachmentLocalIds.includes(attachment.localId)
            );
            return {
                attachments: attachments
                    ? attachments.map(attachment => attachment.__state)
                    : undefined,
            };
        }, {
            compareDepth: {
                attachments: 1,
            },
        });
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {mail.attachment[]}
     */
    get attachments() {
        return this.env.models['mail.attachment'].all().filter(attachment =>
            this.props.attachmentLocalIds.includes(attachment.localId)
        );
    }

    /**
     * @returns {mail.attachment[]}
     */
    get imageAttachments() {
        return this.attachments.filter(attachment => attachment.fileType === 'image');
    }

    /**
     * @returns {mail.attachment[]}
     */
    get nonImageAttachments() {
        return this.attachments.filter(attachment => attachment.fileType !== 'image');
    }

    /**
     * @returns {mail.attachment[]}
     */
    get viewableAttachments() {
        return this.attachments.filter(attachment => attachment.isViewable);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(AttachmentList, {
    props: { record: Object },
    template: 'mail.AttachmentList',
});

registerMessagingComponent(AttachmentList);
