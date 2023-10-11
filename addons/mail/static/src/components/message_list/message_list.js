/** @odoo-module **/

<<<<<<< HEAD
import { useComponentToModel } from '@mail/component_hooks/use_component_to_model';
import { useRenderedValues } from '@mail/component_hooks/use_rendered_values';
import { useUpdate } from '@mail/component_hooks/use_update';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    Message: require('mail/static/src/components/message/message.js'),
};
const useRefs = require('mail/static/src/component_hooks/use_refs/use_refs.js');
const useRenderedValues = require('mail/static/src/component_hooks/use_rendered_values/use_rendered_values.js');
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
const useUpdate = require('mail/static/src/component_hooks/use_update/use_update.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

import { Transition } from "@web/core/transition";

const { Component, onWillPatch, useRef } = owl;

export class MessageList extends Component {

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
            const threadView = this.env.models['mail.thread_view'].get(props.threadViewLocalId);
            const thread = threadView ? threadView.thread : undefined;
            const threadCache = threadView ? threadView.threadCache : undefined;
            return {
                isDeviceMobile: this.env.messaging.device.isMobile,
                thread,
                threadCache,
                threadCacheIsAllHistoryLoaded: threadCache && threadCache.isAllHistoryLoaded,
                threadCacheIsLoaded: threadCache && threadCache.isLoaded,
                threadCacheIsLoadingMore: threadCache && threadCache.isLoadingMore,
                threadCacheLastMessage: threadCache && threadCache.lastMessage,
                threadCacheOrderedMessages: threadCache ? threadCache.orderedMessages : [],
                threadIsTemporary: thread && thread.isTemporary,
                threadMainCache: thread && thread.mainCache,
                threadMessageAfterNewMessageSeparator: thread && thread.messageAfterNewMessageSeparator,
                threadViewComponentHintList: threadView ? threadView.componentHintList : [],
                threadViewNonEmptyMessagesLength: threadView && threadView.nonEmptyMessages.length,
            };
        }, {
            compareDepth: {
                threadCacheOrderedMessages: 1,
                threadViewComponentHintList: 1,
            },
        });
        this._getRefs = useRefs();
        /**
         * States whether there was at least one programmatic scroll since the
         * last scroll event was handled (which is particularly async due to
         * throttled behavior).
         * Useful to avoid loading more messages or to incorrectly disabling the
         * auto-scroll feature when the scroll was not made by the user.
         */
        this._isLastScrollProgrammatic = false;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        /**
         * Reference of the "load more" item. Useful to trigger load more
         * on scroll when it becomes visible.
         */
        this._loadMoreRef = useRef('loadMore');
        /**
         * Snapshot computed during willPatch, which is used by patched.
         */
        this._willPatchSnapshot = undefined;
        this._onScrollThrottled = _.throttle(this._onScrollThrottled.bind(this), 100);
        /**
         * State used by the component at the time of the render. Useful to
         * properly handle async code.
         */
        this._lastRenderedValues = useRenderedValues(() => {
<<<<<<< HEAD
            const messageListView = this.messageListView;
            const threadView = messageListView.threadViewOwner;
=======
            const threadView = this.threadView;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            const thread = threadView && threadView.thread;
            const threadCache = threadView && threadView.threadCache;
            return {
                componentHintList: threadView ? [...threadView.componentHintList] : [],
                hasAutoScrollOnMessageReceived: threadView && threadView.hasAutoScrollOnMessageReceived,
<<<<<<< HEAD
                messageListView,
                order: threadView && threadView.order,
=======
                hasScrollAdjust: this.props.hasScrollAdjust,
                mainCache: thread && thread.mainCache,
                order: this.props.order,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                orderedMessages: threadCache ? [...threadCache.orderedMessages] : [],
                thread,
                threadCache,
                threadCacheInitialScrollHeight: threadView && threadView.threadCacheInitialScrollHeight,
                threadCacheInitialScrollPosition: threadView && threadView.threadCacheInitialScrollPosition,
<<<<<<< HEAD
            };
        });
        // useUpdate must be defined after useRenderedValues, indeed they both
        // use onMounted/onPatched, and the calls from useRenderedValues must
        // happen first to save the values before useUpdate accesses them.
        useUpdate({ func: () => this._update() });
        onWillPatch(() => this._willPatch());
    }

    _willPatch() {
        const lastRenderedValues = this._lastRenderedValues();
        if (!lastRenderedValues) {
            // TODO ABD: REMOVE (traceback in Knowledge to investigate)
            return;
        }
        const { messageListView } = lastRenderedValues;
        if (!messageListView.exists()) {
            return;
        }
        this._willPatchSnapshot = {
            scrollHeight: messageListView.getScrollableElement().scrollHeight,
            scrollTop: messageListView.getScrollableElement().scrollTop,
=======
                threadView,
                threadViewer: threadView && threadView.threadViewer,
            };
        });
        // useUpdate must be defined after useRenderedValues to guarantee proper
        // call order
        useUpdate({ func: () => this._update() });
    }

    willPatch() {
        const lastMessageRef = this.lastMessageRef;
        this._willPatchSnapshot = {
            isLastMessageVisible:
                lastMessageRef &&
                lastMessageRef.isBottomVisible({ offset: 10 }),
            scrollHeight: this._getScrollableElement().scrollHeight,
            scrollTop: this._getScrollableElement().scrollTop,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        };
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Update the scroll position of the message list.
     * This is not done in patched/mounted hooks because scroll position is
     * dependent on UI globally. To illustrate, imagine following UI:
     *
     * +----------+ < viewport top = scrollable top
     * | message  |
     * |   list   |
     * |          |
     * +----------+ < scrolltop = viewport bottom = scrollable bottom
     *
     * Now if a composer is mounted just below the message list, it is shrinked
     * and scrolltop is altered as a result:
     *
     * +----------+ < viewport top = scrollable top
     * | message  |
     * |   list   | < scrolltop = viewport bottom  <-+
     * |          |                                  |-- dist = composer height
     * +----------+ < scrollable bottom            <-+
     * +----------+
     * | composer |
     * +----------+
     *
     * Because of this, the scroll position must be changed when whole UI
     * is rendered. To make this simpler, this is done when <ThreadView/>
     * component is patched. This is acceptable when <ThreadView/> has a
     * fixed height, which is the case for the moment. task-2358066
     */
    adjustFromComponentHints() {
<<<<<<< HEAD
        const { componentHintList, messageListView } = this._lastRenderedValues();
        if (!messageListView.exists()) {
            return;
        }
        for (const hint of componentHintList) {
            switch (hint.type) {
                case 'change-of-thread-cache':
                case 'member-list-hidden':
=======
        const { componentHintList, threadView } = this._lastRenderedValues();
        for (const hint of componentHintList) {
            switch (hint.type) {
                case 'change-of-thread-cache':
                case 'home-menu-hidden':
                case 'home-menu-shown':
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                case 'adjust-scroll':
                    // thread just became visible, the goal is to restore its
                    // saved position if it exists or scroll to the end
                    this._adjustScrollFromModel();
                    break;
<<<<<<< HEAD
                case 'message-posted':
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                case 'message-received':
                case 'messages-loaded':
                case 'new-messages-loaded':
                    // messages have been added at the end, either scroll to the
                    // end or keep the current position
                    this._adjustScrollForExtraMessagesAtTheEnd();
                    break;
                case 'more-messages-loaded':
                    // messages have been added at the start, keep the current
                    // position
                    this._adjustScrollForExtraMessagesAtTheStart();
                    break;
            }
<<<<<<< HEAD
            messageListView.threadViewOwner.markComponentHintProcessed(hint);
=======
            if (threadView && threadView.exists()) {
                threadView.markComponentHintProcessed(hint);
            }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        this._willPatchSnapshot = undefined;
    }

    /**
<<<<<<< HEAD
     * @param {integer} value
     */
    setScrollTop(value) {
        const { messageListView } = this._lastRenderedValues();
        if (messageListView.getScrollableElement().scrollTop === value) {
            return;
        }
        messageListView.update({ isLastScrollProgrammatic: true });
        messageListView.getScrollableElement().scrollTop = value;
=======
     * @param {mail.message} message
     * @returns {string}
     */
    getDateDay(message) {
        if (!message.date) {
            // Without a date, we assume that it's a today message. This is
            // mainly done to avoid flicker inside the UI.
            return this.env._t("Today");
        }
        const date = message.date.format('YYYY-MM-DD');
        if (date === moment().format('YYYY-MM-DD')) {
            return this.env._t("Today");
        } else if (
            date === moment()
                .subtract(1, 'days')
                .format('YYYY-MM-DD')
        ) {
            return this.env._t("Yesterday");
        }
        return message.date.format('LL');
    }

    /**
     * @returns {integer}
     */
    getScrollHeight() {
        return this._getScrollableElement().scrollHeight;
    }

    /**
     * @returns {integer}
     */
    getScrollTop() {
        return this._getScrollableElement().scrollTop;
    }

    /**
     * @returns {mail/static/src/components/message/message.js|undefined}
     */
    get mostRecentMessageRef() {
        const { order } = this._lastRenderedValues();
        if (order === 'desc') {
            return this.messageRefs[0];
        }
        const { length: l, [l - 1]: mostRecentMessageRef } = this.messageRefs;
        return mostRecentMessageRef;
    }

    /**
     * @param {integer} messageId
     * @returns {mail/static/src/components/message/message.js|undefined}
     */
    messageRefFromId(messageId) {
        return this.messageRefs.find(ref => ref.message.id === messageId);
    }

    /**
     * Get list of sub-components Message, ordered based on prop `order`
     * (ASC/DESC).
     *
     * The asynchronous nature of OWL rendering pipeline may reveal disparity
     * between knowledgeable state of store between components. Use this getter
     * with extreme caution!
     *
     * Let's illustrate the disparity with a small example:
     *
     * - Suppose this component is aware of ordered (record) messages with
     *   following IDs: [1, 2, 3, 4, 5], and each (sub-component) messages map
     * each of these records.
     * - Now let's assume a change in store that translate to ordered (record)
     *   messages with following IDs: [2, 3, 4, 5, 6].
     * - Because store changes trigger component re-rendering by their "depth"
     *   (i.e. from parents to children), this component may be aware of
     *   [2, 3, 4, 5, 6] but not yet sub-components, so that some (component)
     *   messages should be destroyed but aren't yet (the ref with message ID 1)
     *   and some do not exist yet (no ref with message ID 6).
     *
     * @returns {mail/static/src/components/message/message.js[]}
     */
    get messageRefs() {
        const { order } = this._lastRenderedValues();
        const refs = this._getRefs();
        const ascOrderedMessageRefs = Object.entries(refs)
            .filter(([refId, ref]) => (
                    // Message refs have message local id as ref id, and message
                    // local ids contain name of model 'mail.message'.
                    refId.includes(this.env.models['mail.message'].modelName) &&
                    // Component that should be destroyed but haven't just yet.
                    ref.message
                )
            )
            .map(([refId, ref]) => ref)
            .sort((ref1, ref2) => (ref1.message.id < ref2.message.id ? -1 : 1));
        if (order === 'desc') {
            return ascOrderedMessageRefs.reverse();
        }
        return ascOrderedMessageRefs;
    }

    /**
     * @returns {mail.message[]}
     */
    get orderedMessages() {
        const threadCache = this.threadView.threadCache;
        if (this.props.order === 'desc') {
            return [...threadCache.orderedMessages].reverse();
        }
        return threadCache.orderedMessages;
    }

    /**
     * @param {integer} value
     */
    setScrollTop(value) {
        if (this._getScrollableElement().scrollTop === value) {
            return;
        }
        this._isLastScrollProgrammatic = true;
        this._getScrollableElement().scrollTop = value;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    /**
     * @returns {MessageListView}
     */
<<<<<<< HEAD
    get messageListView() {
        return this.props.record;
=======
    shouldMessageBeSquashed(prevMessage, message) {
        if (!this.props.hasSquashCloseMessages) {
            return false;
        }
        if (!prevMessage.date && message.date) {
            return false;
        }
        if (message.date && prevMessage.date && Math.abs(message.date.diff(prevMessage.date)) > 60000) {
            // more than 1 min. elasped
            return false;
        }
        if (prevMessage.message_type !== 'comment' || message.message_type !== 'comment') {
            return false;
        }
        if (prevMessage.author !== message.author) {
            // from a different author
            return false;
        }
        if (prevMessage.originThread !== message.originThread) {
            return false;
        }
        if (
            prevMessage.moderation_status === 'pending_moderation' ||
            message.moderation_status === 'pending_moderation'
        ) {
            return false;
        }
        if (
            prevMessage.notifications.length > 0 ||
            message.notifications.length > 0
        ) {
            // visual about notifications is restricted to non-squashed messages
            return false;
        }
        const prevOriginThread = prevMessage.originThread;
        const originThread = message.originThread;
        if (
            prevOriginThread &&
            originThread &&
            prevOriginThread.model === originThread.model &&
            originThread.model !== 'mail.channel' &&
            prevOriginThread.id !== originThread.id
        ) {
            // messages linked to different document thread
            return false;
        }
        return true;
    }

    /**
     * @returns {mail.thread_view}
     */
    get threadView() {
        return this.env.models['mail.thread_view'].get(this.props.threadViewLocalId);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _adjustScrollForExtraMessagesAtTheEnd() {
        const {
            hasAutoScrollOnMessageReceived,
<<<<<<< HEAD
            messageListView,
            order,
        } = this._lastRenderedValues();
        if (!messageListView.getScrollableElement() || !messageListView.hasScrollAdjust) {
=======
            hasScrollAdjust,
            order,
        } = this._lastRenderedValues();
        if (!this._getScrollableElement() || !hasScrollAdjust) {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            return;
        }
        if (!hasAutoScrollOnMessageReceived) {
            if (order === 'desc' && this._willPatchSnapshot) {
                const { scrollHeight, scrollTop } = this._willPatchSnapshot;
<<<<<<< HEAD
                this.setScrollTop(messageListView.getScrollableElement().scrollHeight - scrollHeight + scrollTop);
=======
                this.setScrollTop(this._getScrollableElement().scrollHeight - scrollHeight + scrollTop);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
            return;
        }
        this._scrollToEnd();
    }

    /**
     * @private
     */
    _adjustScrollForExtraMessagesAtTheStart() {
        const {
<<<<<<< HEAD
            messageListView,
            order,
        } = this._lastRenderedValues();
        if (
            !messageListView.getScrollableElement() ||
            !messageListView.hasScrollAdjust ||
=======
            hasScrollAdjust,
            order,
        } = this._lastRenderedValues();
        if (
            !this._getScrollableElement() ||
            !hasScrollAdjust ||
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            !this._willPatchSnapshot ||
            order === 'desc'
        ) {
            return;
        }
        const { scrollHeight, scrollTop } = this._willPatchSnapshot;
<<<<<<< HEAD
        this.setScrollTop(messageListView.getScrollableElement().scrollHeight - scrollHeight + scrollTop);
=======
        this.setScrollTop(this._getScrollableElement().scrollHeight - scrollHeight + scrollTop);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    /**
     * @private
     */
    _adjustScrollFromModel() {
        const {
<<<<<<< HEAD
            messageListView,
            threadCacheInitialScrollHeight,
            threadCacheInitialScrollPosition,
        } = this._lastRenderedValues();
        if (!messageListView.getScrollableElement() || !messageListView.hasScrollAdjust) {
=======
            hasScrollAdjust,
            threadCacheInitialScrollHeight,
            threadCacheInitialScrollPosition,
        } = this._lastRenderedValues();
        if (!this._getScrollableElement() || !hasScrollAdjust) {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            return;
        }
        if (
            threadCacheInitialScrollPosition !== undefined &&
<<<<<<< HEAD
            messageListView.getScrollableElement().scrollHeight === threadCacheInitialScrollHeight
=======
            this._getScrollableElement().scrollHeight === threadCacheInitialScrollHeight
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        ) {
            this.setScrollTop(threadCacheInitialScrollPosition);
            return;
        }
        this._scrollToEnd();
        return;
    }

    /**
     * @private
     */
    _checkMostRecentMessageIsVisible() {
<<<<<<< HEAD
        const { messageListView } = this._lastRenderedValues();
        if (!messageListView.exists()) {
            return;
        }
        const { lastMessageListViewItem } = messageListView.threadViewOwner;
        if (lastMessageListViewItem && lastMessageListViewItem.isPartiallyVisible()) {
            messageListView.threadViewOwner.handleVisibleMessage(lastMessageListViewItem.message);
=======
        const {
            mainCache,
            threadCache,
            threadView,
        } = this._lastRenderedValues();
        if (!threadView || !threadView.exists()) {
            return;
        }
        const lastMessageIsVisible =
            threadCache &&
            this.mostRecentMessageRef &&
            threadCache === mainCache &&
            this.mostRecentMessageRef.isPartiallyVisible();
        if (lastMessageIsVisible) {
            threadView.handleVisibleMessage(this.mostRecentMessageRef.message);
        }
    }

    /**
     * @private
     * @returns {Element|undefined} Scrollable Element
     */
    _getScrollableElement() {
        if (this.props.getScrollableElement) {
            return this.props.getScrollableElement();
        } else {
            return this.el;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
    }

    /**
     * @private
     * @returns {boolean}
     */
    _isLoadMoreVisible() {
        const { messageListView } = this._lastRenderedValues();
        const loadMore = this._loadMoreRef.el;
        if (!loadMore) {
            return false;
        }
        const loadMoreRect = loadMore.getBoundingClientRect();
<<<<<<< HEAD
        const elRect = messageListView.getScrollableElement().getBoundingClientRect();
=======
        const elRect = this._getScrollableElement().getBoundingClientRect();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        const isInvisible = loadMoreRect.top > elRect.bottom || loadMoreRect.bottom < elRect.top;
        return !isInvisible;
    }

    /**
     * Scrolls to the end of the list.
     *
     * @private
     */
<<<<<<< HEAD
    _scrollToEnd() {
        const { messageListView, order } = this._lastRenderedValues();
        this.setScrollTop(order === 'asc' ? messageListView.getScrollableElement().scrollHeight - messageListView.getScrollableElement().clientHeight : 0);
=======
    _loadMore() {
        const { threadCache } = this._lastRenderedValues();
        if (!threadCache || !threadCache.exists()) {
            return;
        }
        threadCache.loadMoreMessages();
    }

    /**
     * Scrolls to the end of the list.
     *
     * @private
     */
    _scrollToEnd() {
        const { order } = this._lastRenderedValues();
        this.setScrollTop(order === 'asc' ? this._getScrollableElement().scrollHeight - this._getScrollableElement().clientHeight : 0);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    /**
     * @private
     */
    _update() {
<<<<<<< HEAD
=======
        this._checkMostRecentMessageIsVisible();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        this.adjustFromComponentHints();
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {ScrollEvent} ev
     */
    onScroll(ev) {
        this._onScrollThrottled(ev);
    }

    /**
     * @private
     * @param {ScrollEvent} ev
     */
<<<<<<< HEAD
    _onScrollThrottled(ev) {
        const {
            messageListView,
            orderedMessages,
            thread,
            threadCache,
        } = this._lastRenderedValues();
        if (!messageListView.exists()) {
            return;
        }
        if (!messageListView.getScrollableElement()) {
            // could be unmounted in the meantime (due to throttled behavior)
            return;
        }
        const scrollTop = messageListView.getScrollableElement().scrollTop;
        this.messaging.messagingBus.trigger('o-component-message-list-scrolled', {
            orderedMessages,
            scrollTop,
            thread,
            threadViewer: messageListView.threadViewOwner.threadViewer,
        });
        messageListView.update({
            clientHeight: messageListView.getScrollableElement().clientHeight,
            scrollHeight: messageListView.getScrollableElement().scrollHeight,
            scrollTop: messageListView.getScrollableElement().scrollTop,
        });
        if (!messageListView.isLastScrollProgrammatic) {
            // Automatically scroll to new received messages only when the list is
            // currently fully scrolled.
            const hasAutoScrollOnMessageReceived = messageListView.isAtEnd;
            messageListView.threadViewOwner.update({ hasAutoScrollOnMessageReceived });
        }
        messageListView.threadViewOwner.threadViewer.saveThreadCacheScrollHeightAsInitial(messageListView.getScrollableElement().scrollHeight, threadCache);
        messageListView.threadViewOwner.threadViewer.saveThreadCacheScrollPositionsAsInitial(scrollTop, threadCache);
        if (
            !messageListView.isLastScrollProgrammatic &&
            this._isLoadMoreVisible() &&
            threadCache &&
            threadCache.exists()
        ) {
            threadCache.loadMoreMessages();
        }
        this._checkMostRecentMessageIsVisible();
        messageListView.update({ isLastScrollProgrammatic: false });
=======
    onScroll(ev) {
        this._onScrollThrottled(ev);
    }

    /**
     * @private
     * @param {ScrollEvent} ev
     */
    _onScrollThrottled(ev) {
        const {
            order,
            orderedMessages,
            thread,
            threadCache,
            threadView,
            threadViewer,
        } = this._lastRenderedValues();
        if (!this._getScrollableElement()) {
            // could be unmounted in the meantime (due to throttled behavior)
            return;
        }
        const scrollTop = this._getScrollableElement().scrollTop;
        this.env.messagingBus.trigger('o-component-message-list-scrolled', {
            orderedMessages,
            scrollTop,
            thread,
            threadViewer,
        });
        if (!this._isLastScrollProgrammatic && threadView && threadView.exists()) {
            // Margin to compensate for inaccurate scrolling to bottom and height
            // flicker due height change of composer area.
            const margin = 30;
            // Automatically scroll to new received messages only when the list is
            // currently fully scrolled.
            const hasAutoScrollOnMessageReceived = (order === 'asc')
                ? scrollTop >= this._getScrollableElement().scrollHeight - this._getScrollableElement().clientHeight - margin
                : scrollTop <= margin;
            threadView.update({ hasAutoScrollOnMessageReceived });
        }
        if (threadViewer && threadViewer.exists()) {
            threadViewer.saveThreadCacheScrollHeightAsInitial(this._getScrollableElement().scrollHeight, threadCache);
            threadViewer.saveThreadCacheScrollPositionsAsInitial(scrollTop, threadCache);
        }
        if (!this._isLastScrollProgrammatic && this._isLoadMoreVisible()) {
            this._loadMore();
        }
        this._checkMostRecentMessageIsVisible();
        this._isLastScrollProgrammatic = false;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(MessageList, {
<<<<<<< HEAD
    components: { Transition },
    props: { record: Object },
=======
    components,
    defaultProps: {
        hasMessageCheckbox: false,
        hasScrollAdjust: true,
        hasSquashCloseMessages: false,
        haveMessagesMarkAsReadIcon: false,
        haveMessagesReplyIcon: false,
        order: 'asc',
    },
    props: {
        hasMessageCheckbox: Boolean,
        hasSquashCloseMessages: Boolean,
        haveMessagesMarkAsReadIcon: Boolean,
        haveMessagesReplyIcon: Boolean,
        hasScrollAdjust: Boolean,
        /**
         * Function returns the exact scrollable element from the parent
         * to manage proper scroll heights which affects the load more messages.
         */
        getScrollableElement: {
            type: Function,
            optional: true,
        },
        order: {
            type: String,
            validate: prop => ['asc', 'desc'].includes(prop),
        },
        selectedMessageLocalId: {
            type: String,
            optional: true,
        },
        threadViewLocalId: String,
    },
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    template: 'mail.MessageList',
});

registerMessagingComponent(MessageList);
