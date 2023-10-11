/** @odoo-module **/

<<<<<<< HEAD
import { useUpdate } from '@mail/component_hooks/use_update';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    AutocompleteInput: require('mail/static/src/components/autocomplete_input/autocomplete_input.js'),
    ChatWindowHeader: require('mail/static/src/components/chat_window_header/chat_window_header.js'),
    ThreadView: require('mail/static/src/components/thread_view/thread_view.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
const useUpdate = require('mail/static/src/component_hooks/use_update/use_update.js');
const { isEventHandled } = require('mail/static/src/utils/utils.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const patchMixin = require('web.patchMixin');

const { Component } = owl;

export class ChatWindow extends Component {

    /**
     * @override
     */
<<<<<<< HEAD
    setup() {
        super.setup();
        useUpdate({ func: () => this._update() });
=======
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const chatWindow = this.env.models['mail.chat_window'].get(props.chatWindowLocalId);
            const thread = chatWindow ? chatWindow.thread : undefined;
            return {
                chatWindow,
                chatWindowHasNewMessageForm: chatWindow && chatWindow.hasNewMessageForm,
                chatWindowIsDoFocus: chatWindow && chatWindow.isDoFocus,
                chatWindowIsFocused: chatWindow && chatWindow.isFocused,
                chatWindowIsFolded: chatWindow && chatWindow.isFolded,
                chatWindowThreadView: chatWindow && chatWindow.threadView,
                chatWindowVisibleIndex: chatWindow && chatWindow.visibleIndex,
                chatWindowVisibleOffset: chatWindow && chatWindow.visibleOffset,
                isDeviceMobile: this.env.messaging.device.isMobile,
                localeTextDirection: this.env.messaging.locale.textDirection,
                thread,
                threadMassMailing: thread && thread.mass_mailing,
                threadModel: thread && thread.model,
            };
        });
        useUpdate({ func: () => this._update() });
        /**
         * Reference of the header of the chat window.
         * Useful to prevent click on header from wrongly focusing the window.
         */
        this._chatWindowHeaderRef = useRef('header');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        /**
         * Reference of the autocomplete input (new_message chat window only).
         * Useful when focusing this chat window, which consists of focusing
         * this input.
         */
<<<<<<< HEAD
        this._inputRef = { el: null };
        // the following are passed as props to children
=======
        this._inputRef = useRef('input');
        /**
         * Reference of thread in the chat window (chat window with thread
         * only). Useful when focusing this chat window, which consists of
         * focusing this thread. Will likely focus the composer of thread, if
         * it has one!
         */
        this._threadRef = useRef('thread');
        this._onWillHideHomeMenu = this._onWillHideHomeMenu.bind(this);
        this._onWillShowHomeMenu = this._onWillShowHomeMenu.bind(this);
        // the following are passed as props to children
        this._onAutocompleteSelect = this._onAutocompleteSelect.bind(this);
        this._onAutocompleteSource = this._onAutocompleteSource.bind(this);
        this._saveThreadScrollTop = this._saveThreadScrollTop.bind(this);
        this._constructor(...args);
    }

    /**
     * Allows patching constructor.
     */
    _constructor() {}

    mounted() {
        this.env.messagingBus.on('will_hide_home_menu', this, this._onWillHideHomeMenu);
        this.env.messagingBus.on('will_show_home_menu', this, this._onWillShowHomeMenu);
    }

    willUnmount() {
        this.env.messagingBus.off('will_hide_home_menu', this, this._onWillHideHomeMenu);
        this.env.messagingBus.off('will_show_home_menu', this, this._onWillShowHomeMenu);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {ChatWindow}
     */
    get chatWindow() {
        return this.props.record;
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
<<<<<<< HEAD
=======
     * Apply visual position of the chat window.
     *
     * @private
     */
    _applyVisibleOffset() {
        const textDirection = this.env.messaging.locale.textDirection;
        const offsetFrom = textDirection === 'rtl' ? 'left' : 'right';
        const oppositeFrom = offsetFrom === 'right' ? 'left' : 'right';
        this.el.style[offsetFrom] = this.chatWindow.visibleOffset + 'px';
        this.el.style[oppositeFrom] = 'auto';
    }

    /**
     * Focus this chat window.
     *
     * @private
     */
    _focus() {
        this.chatWindow.update({
            isDoFocus: false,
            isFocused: true,
        });
        if (this._inputRef.comp) {
            this._inputRef.comp.focus();
        }
        if (this._threadRef.comp) {
            this._threadRef.comp.focus();
        }
    }

    /**
     * Save the scroll positions of the chat window in the store.
     * This is useful in order to remount chat windows and keep previous
     * scroll positions. This is necessary because when toggling on/off
     * home menu, the chat windows have to be remade from scratch.
     *
     * @private
     */
    _saveThreadScrollTop() {
        if (
            !this._threadRef.comp ||
            !this.chatWindow.threadViewer ||
            !this.chatWindow.threadViewer.threadView
        ) {
            return;
        }
        if (this.chatWindow.threadViewer.threadView.componentHintList.length > 0) {
            // the current scroll position is likely incorrect due to the
            // presence of hints to adjust it
            return;
        }
        this.chatWindow.threadViewer.saveThreadCacheScrollHeightAsInitial(
            this._threadRef.comp.getScrollHeight()
        );
        this.chatWindow.threadViewer.saveThreadCacheScrollPositionsAsInitial(
            this._threadRef.comp.getScrollTop()
        );
    }

    /**
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
     * @private
     */
    _update() {
        if (!this.root.el) {
            return;
        }
        if (this.chatWindow.isDoFocus) {
<<<<<<< HEAD
            this.chatWindow.update({ isDoFocus: false });
            if (
                this.chatWindow.newMessageAutocompleteInputView &&
                this.chatWindow.newMessageAutocompleteInputView.component &&
                this.chatWindow.newMessageAutocompleteInputView.component.root.el
            ) {
                this.chatWindow.newMessageAutocompleteInputView.component.root.el.focus();
            }
        }
=======
            this._focus();
        }
        this._applyVisibleOffset();
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called when selecting an item in the autocomplete input of the
     * 'new_message' chat window.
     *
     * @private
     * @param {Event} ev
     * @param {Object} ui
     * @param {Object} ui.item
     * @param {integer} ui.item.id
     */
    async _onAutocompleteSelect(ev, ui) {
        const chat = await this.env.messaging.getChat({ partnerId: ui.item.id });
        if (!chat) {
            return;
        }
        this.env.messaging.chatWindowManager.openThread(chat, {
            makeActive: true,
            replaceNewMessage: true,
        });
    }

    /**
     * Called when typing in the autocomplete input of the 'new_message' chat
     * window.
     *
     * @private
     * @param {Object} req
     * @param {string} req.term
     * @param {function} res
     */
    _onAutocompleteSource(req, res) {
        this.env.models['mail.partner'].imSearch({
            callback: (partners) => {
                const suggestions = partners.map(partner => {
                    return {
                        id: partner.id,
                        value: partner.nameOrDisplayName,
                        label: partner.nameOrDisplayName,
                    };
                });
                res(_.sortBy(suggestions, 'label'));
            },
            keyword: _.escape(req.term),
            limit: 10,
        });
    }

    /**
     * Called when clicking on header of chat window. Usually folds the chat
     * window.
     *
     * @private
     * @param {CustomEvent} ev
     */
    _onClickedHeader(ev) {
        ev.stopPropagation();
        if (this.env.messaging.device.isMobile) {
            return;
        }
        if (this.chatWindow.isFolded) {
            this.chatWindow.unfold();
            this.chatWindow.focus();
        } else {
            this._saveThreadScrollTop();
            this.chatWindow.fold();
        }
    }

    /**
     * Called when an element in the thread becomes focused.
     *
     * @private
     * @param {FocusEvent} ev
     */
    _onFocusinThread(ev) {
        ev.stopPropagation();
        if (!this.chatWindow) {
            // prevent crash on destroy
            return;
        }
        this.chatWindow.update({ isFocused: true });
    }

    /**
     * Focus out the chat window.
     *
     * @private
     */
    _onFocusout() {
        if (!this.chatWindow) {
            // ignore focus out due to record being deleted
            return;
        }
        this.chatWindow.update({ isFocused: false });
    }

    /**
     * @private
     * @param {KeyboardEvent} ev
     */
    _onKeydown(ev) {
        if (!this.chatWindow) {
            // prevent crash during delete
            return;
        }
        switch (ev.key) {
            case 'Tab':
                ev.preventDefault();
                if (ev.shiftKey) {
                    this.chatWindow.focusPreviousVisibleUnfoldedChatWindow();
                } else {
                    this.chatWindow.focusNextVisibleUnfoldedChatWindow();
                }
                break;
            case 'Escape':
                if (isEventHandled(ev, 'ComposerTextInput.closeSuggestions')) {
                    break;
                }
                if (isEventHandled(ev, 'Composer.closeEmojisPopover')) {
                    break;
                }
                ev.preventDefault();
                this.chatWindow.focusNextVisibleUnfoldedChatWindow();
                this.chatWindow.close();
                break;
        }
    }

    /**
     * Save the scroll positions of the chat window in the store.
     * This is useful in order to remount chat windows and keep previous
     * scroll positions. This is necessary because when toggling on/off
     * home menu, the chat windows have to be remade from scratch.
     *
     * @private
     */
    async _onWillHideHomeMenu() {
        this._saveThreadScrollTop();
    }

    /**
     * Save the scroll positions of the chat window in the store.
     * This is useful in order to remount chat windows and keep previous
     * scroll positions. This is necessary because when toggling on/off
     * home menu, the chat windows have to be remade from scratch.
     *
     * @private
     */
    async _onWillShowHomeMenu() {
        this._saveThreadScrollTop();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(ChatWindow, {
    props: { record: Object },
    template: 'mail.ChatWindow',
});

<<<<<<< HEAD
registerMessagingComponent(ChatWindow);
=======
return patchMixin(ChatWindow);

});
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
