/** @odoo-module **/

<<<<<<< HEAD
import { useRefToModel } from '@mail/component_hooks/use_ref_to_model';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    MessageAuthorPrefix: require('mail/static/src/components/message_author_prefix/message_author_prefix.js'),
    PartnerImStatusIcon: require('mail/static/src/components/partner_im_status_icon/partner_im_status_icon.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
const mailUtils = require('mail.utils');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

export class ThreadNeedactionPreview extends Component {

    /**
     * @override
     */
<<<<<<< HEAD
    setup() {
        super.setup();
        useRefToModel({ fieldName: 'markAsReadRef', refName: 'markAsRead' });
=======
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const thread = this.env.models['mail.thread'].get(props.threadLocalId);
            const mainThreadCache = thread ? thread.mainCache : undefined;
            let lastNeedactionMessageAsOriginThreadAuthor;
            let lastNeedactionMessageAsOriginThread;
            let threadCorrespondent;
            if (thread) {
                lastNeedactionMessageAsOriginThread = mainThreadCache.lastNeedactionMessageAsOriginThread;
                threadCorrespondent = thread.correspondent;
            }
            if (lastNeedactionMessageAsOriginThread) {
                lastNeedactionMessageAsOriginThreadAuthor = lastNeedactionMessageAsOriginThread.author;
            }
            return {
                isDeviceMobile: this.env.messaging.device.isMobile,
                lastNeedactionMessageAsOriginThread: lastNeedactionMessageAsOriginThread ? lastNeedactionMessageAsOriginThread.__state : undefined,
                lastNeedactionMessageAsOriginThreadAuthor: lastNeedactionMessageAsOriginThreadAuthor
                    ? lastNeedactionMessageAsOriginThreadAuthor.__state
                    : undefined,
                thread: thread ? thread.__state : undefined,
                threadCorrespondent: threadCorrespondent
                    ? threadCorrespondent.__state
                    : undefined,
            };
        });
        /**
         * Reference of the "mark as read" button. Useful to disable the
         * top-level click handler when clicking on this specific button.
         */
        this._markAsReadRef = useRef('markAsRead');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Get the image route of the thread.
     *
     * @returns {string}
     */
    image() {
        if (this.threadNeedactionPreviewView.thread.moduleIcon) {
            return this.threadNeedactionPreviewView.thread.moduleIcon;
        }
<<<<<<< HEAD
        if (!this.threadNeedactionPreviewView.thread.channel) {
            return '/mail/static/src/img/smiley/avatar.jpg';
=======
        if (this.thread.correspondent) {
            return this.thread.correspondent.avatarUrl;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        if (this.threadNeedactionPreviewView.thread.channel.correspondent) {
            return this.threadNeedactionPreviewView.thread.channel.correspondent.avatarUrl;
        }
        return `/web/image/mail.channel/${this.threadNeedactionPreviewView.thread.id}/avatar_128?unique=${this.threadNeedactionPreviewView.thread.channel.avatarCacheKey}`;
    }

    /**
     * @returns {ThreadNeedactionPreviewView}
     */
<<<<<<< HEAD
    get threadNeedactionPreviewView() {
        return this.props.record;
=======
    get inlineLastNeedactionMessageBody() {
        if (!this.thread.lastNeedactionMessage) {
            return '';
        }
        return mailUtils.htmlToTextContentInline(this.thread.lastNeedactionMessage.prettyBody);
    }

    /**
     * Get inline content of the last message of this conversation.
     *
     * @returns {string}
     */
    get inlineLastNeedactionMessageAsOriginThreadBody() {
        if (!this.thread.lastNeedactionMessageAsOriginThread) {
            return '';
        }
        return mailUtils.htmlToTextContentInline(this.thread.lastNeedactionMessageAsOriginThread.prettyBody);
    }

    /**
     * @returns {mail.thread}
     */
    get thread() {
        return this.env.models['mail.thread'].get(this.props.threadLocalId);
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClick(ev) {
        const markAsRead = this._markAsReadRef.el;
        if (markAsRead && markAsRead.contains(ev.target)) {
            // handled in `_onClickMarkAsRead`
            return;
        }
        this.thread.open();
        if (!this.env.messaging.device.isMobile) {
            this.env.messaging.messagingMenu.close();
        }
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickMarkAsRead(ev) {
        this.env.models['mail.message'].markAllAsRead([
            ['model', '=', this.thread.model],
            ['res_id', '=', this.thread.id],
        ]);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(ThreadNeedactionPreview, {
    props: { record: Object },
    template: 'mail.ThreadNeedactionPreview',
});

registerMessagingComponent(ThreadNeedactionPreview);
