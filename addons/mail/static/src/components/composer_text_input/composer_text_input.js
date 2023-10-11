/** @odoo-module **/

<<<<<<< HEAD
import { useRefToModel } from '@mail/component_hooks/use_ref_to_model';
import { useUpdate } from '@mail/component_hooks/use_update';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
const useUpdate = require('mail/static/src/component_hooks/use_update/use_update.js');

const components = {
    ComposerSuggestionList: require('mail/static/src/components/composer_suggestion_list/composer_suggestion_list.js'),
};
const { markEventHandled } = require('mail/static/src/utils/utils.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

<<<<<<< HEAD
export class ComposerTextInput extends Component {
=======
class ComposerTextInput extends Component {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    /**
     * @override
     */
<<<<<<< HEAD
    setup() {
        super.setup();
        useRefToModel({ fieldName: 'mirroredTextareaRef', refName: 'mirroredTextarea' });
        useRefToModel({ fieldName: 'textareaRef', refName: 'textarea' });
        /**
         * Updates the composer text input content when composer is mounted
         * as textarea content can't be changed from the DOM.
         */
        useUpdate({ func: () => this._update() });
=======
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps({
            compareDepth: {
                sendShortcuts: 1,
            },
        });
        useStore(props => {
            const composer = this.env.models['mail.composer'].get(props.composerLocalId);
            const thread = composer && composer.thread;
            return {
                composerHasFocus: composer && composer.hasFocus,
                composerHasSuggestions: composer && composer.hasSuggestions,
                composerIsLog: composer && composer.isLog,
                composerTextInputContent: composer && composer.textInputContent,
                composerTextInputCursorEnd: composer && composer.textInputCursorEnd,
                composerTextInputCursorStart: composer && composer.textInputCursorStart,
                composerTextInputSelectionDirection: composer && composer.textInputSelectionDirection,
                isDeviceMobile: this.env.messaging.device.isMobile,
                threadModel: thread && thread.model,
            };
        });
        /**
         * Updates the composer text input content when composer is mounted
         * as textarea content can't be changed from the DOM.
         */
        useUpdate({ func: () => this._update() });
        /**
         * Last content of textarea from input event. Useful to determine
         * whether the current partner is typing something.
         */
        this._textareaLastInputValue = "";
        /**
         * Reference of the textarea. Useful to set height, selection and content.
         */
        this._textareaRef = useRef('textarea');
        /**
         * This is the invisible textarea used to compute the composer height
         * based on the text content. We need it to downsize the textarea
         * properly without flicker.
         */
        this._mirroredTextareaRef = useRef('mirroredTextarea');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {ComposerView}
     */
<<<<<<< HEAD
    get composerView() {
        return this.props.record;
=======
    get composer() {
        return this.env.models['mail.composer'].get(this.props.composerLocalId);
    }

    /**
     * @returns {string}
     */
    get textareaPlaceholder() {
        if (!this.composer) {
            return "";
        }
        if (this.composer.thread && this.composer.thread.model !== 'mail.channel') {
            if (this.composer.isLog) {
                return this.env._t("Log an internal note...");
            }
            return this.env._t("Send a message to followers...");
        }
        return this.env._t("Write something...");
    }

    focus() {
        this._textareaRef.el.focus();
    }

    focusout() {
        this.saveStateInStore();
        this._textareaRef.el.blur();
    }

    /**
     * Saves the composer text input state in store
     */
    saveStateInStore() {
        this.composer.update({
            textInputContent: this._getContent(),
            textInputCursorEnd: this._getSelectionEnd(),
            textInputCursorStart: this._getSelectionStart(),
            textInputSelectionDirection: this._textareaRef.el.selectionDirection,
        });
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Determines whether the textarea is empty or not.
     *
     * @private
     * @returns {boolean}
     */
    _isEmpty() {
        return this.composerView.textareaRef.el.value === "";
    }

    /**
     * Updates the content and height of a textarea
     *
     * @private
     */
    _update() {
<<<<<<< HEAD
        if (!this.root.el) {
            return;
        }
        if (this.composerView.doFocus) {
            this.composerView.update({ doFocus: false });
            if (this.messaging.device.isSmall) {
                this.root.el.scrollIntoView();
            }
            this.composerView.textareaRef.el.focus();
        }
        if (this.composerView.hasToRestoreContent) {
            this.composerView.textareaRef.el.value = this.composerView.composer.textInputContent;
            if (this.composerView.isFocused) {
                this.composerView.textareaRef.el.setSelectionRange(
                    this.composerView.composer.textInputCursorStart,
                    this.composerView.composer.textInputCursorEnd,
                    this.composerView.composer.textInputSelectionDirection,
                );
            }
            this.composerView.update({ hasToRestoreContent: false });
        }
        this.composerView.updateTextInputHeight();
=======
        if (!this.composer) {
            return;
        }
        if (this.composer.isLastStateChangeProgrammatic) {
            this._textareaRef.el.value = this.composer.textInputContent;
            if (this.composer.hasFocus) {
                this._textareaRef.el.setSelectionRange(
                    this.composer.textInputCursorStart,
                    this.composer.textInputCursorEnd,
                    this.composer.textInputSelectionDirection,
                );
            }
            this.composer.update({ isLastStateChangeProgrammatic: false });
        }
        this._updateHeight();
    }

    /**
     * Updates the textarea height.
     *
     * @private
     */
    _updateHeight() {
        this._mirroredTextareaRef.el.value = this.composer.textInputContent;
        this._textareaRef.el.style.height = (this._mirroredTextareaRef.el.scrollHeight) + "px";
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClickTextarea() {
        // clicking might change the cursor position
        this.saveStateInStore();
    }

    /**
     * @private
     */
    _onFocusinTextarea() {
        this.composer.focus();
        this.trigger('o-focusin-composer');
    }

    /**
     * @private
     */
    _onFocusoutTextarea() {
        this.saveStateInStore();
        this.composer.update({ hasFocus: false });
    }

    /**
     * @private
     */
    _onInputTextarea() {
        this.saveStateInStore();
        if (this._textareaLastInputValue !== this._textareaRef.el.value) {
            this.composer.handleCurrentPartnerIsTyping();
        }
        this._textareaLastInputValue = this._textareaRef.el.value;
        this._updateHeight();
    }

    /**
     * @private
     * @param {KeyboardEvent} ev
     */
    _onKeydownTextarea(ev) {
        switch (ev.key) {
            case 'Escape':
                if (this.composer.hasSuggestions) {
                    ev.preventDefault();
                    this.composer.closeSuggestions();
                    markEventHandled(ev, 'ComposerTextInput.closeSuggestions');
                }
                break;
            // UP, DOWN, TAB: prevent moving cursor if navigation in mention suggestions
            case 'ArrowUp':
            case 'PageUp':
            case 'ArrowDown':
            case 'PageDown':
            case 'Home':
            case 'End':
            case 'Tab':
                if (this.composer.hasSuggestions) {
                    // We use preventDefault here to avoid keys native actions but actions are handled in keyUp
                    ev.preventDefault();
                }
                break;
            // ENTER: submit the message only if the dropdown mention proposition is not displayed
            case 'Enter':
                this._onKeydownTextareaEnter(ev);
                break;
        }
    }

    /**
     * @private
     * @param {KeyboardEvent} ev
     */
    _onKeydownTextareaEnter(ev) {
        if (this.composer.hasSuggestions) {
            ev.preventDefault();
            return;
        }
        if (
            this.props.sendShortcuts.includes('ctrl-enter') &&
            !ev.altKey &&
            ev.ctrlKey &&
            !ev.metaKey &&
            !ev.shiftKey
        ) {
            this.trigger('o-composer-text-input-send-shortcut');
            ev.preventDefault();
            return;
        }
        if (
            this.props.sendShortcuts.includes('enter') &&
            !ev.altKey &&
            !ev.ctrlKey &&
            !ev.metaKey &&
            !ev.shiftKey
        ) {
            this.trigger('o-composer-text-input-send-shortcut');
            ev.preventDefault();
            return;
        }
        if (
            this.props.sendShortcuts.includes('meta-enter') &&
            !ev.altKey &&
            !ev.ctrlKey &&
            ev.metaKey &&
            !ev.shiftKey
        ) {
            this.trigger('o-composer-text-input-send-shortcut');
            ev.preventDefault();
            return;
        }
    }

    /**
     * Key events management is performed in a Keyup to avoid intempestive RPC calls
     *
     * @private
     * @param {KeyboardEvent} ev
     */
    _onKeyupTextarea(ev) {
        switch (ev.key) {
            case 'Escape':
                // already handled in _onKeydownTextarea, break to avoid default
                break;
            // ENTER, HOME, END, UP, DOWN, PAGE UP, PAGE DOWN, TAB: check if navigation in mention suggestions
            case 'Enter':
                if (this.composer.hasSuggestions) {
                    this.composer.insertSuggestion();
                    this.composer.closeSuggestions();
                    this.focus();
                }
                break;
            case 'ArrowUp':
            case 'PageUp':
                if (this.composer.hasSuggestions) {
                    this.composer.setPreviousSuggestionActive();
                    this.composer.update({ hasToScrollToActiveSuggestion: true });
                }
                break;
            case 'ArrowDown':
            case 'PageDown':
                if (this.composer.hasSuggestions) {
                    this.composer.setNextSuggestionActive();
                    this.composer.update({ hasToScrollToActiveSuggestion: true });
                }
                break;
            case 'Home':
                if (this.composer.hasSuggestions) {
                    this.composer.setFirstSuggestionActive();
                    this.composer.update({ hasToScrollToActiveSuggestion: true });
                }
                break;
            case 'End':
                if (this.composer.hasSuggestions) {
                    this.composer.setLastSuggestionActive();
                    this.composer.update({ hasToScrollToActiveSuggestion: true });
                }
                break;
            case 'Tab':
                if (this.composer.hasSuggestions) {
                    if (ev.shiftKey) {
                        this.composer.setPreviousSuggestionActive();
                        this.composer.update({ hasToScrollToActiveSuggestion: true });
                    } else {
                        this.composer.setNextSuggestionActive();
                        this.composer.update({ hasToScrollToActiveSuggestion: true });
                    }
                }
                break;
            case 'Alt':
            case 'AltGraph':
            case 'CapsLock':
            case 'Control':
            case 'Fn':
            case 'FnLock':
            case 'Hyper':
            case 'Meta':
            case 'NumLock':
            case 'ScrollLock':
            case 'Shift':
            case 'ShiftSuper':
            case 'Symbol':
            case 'SymbolLock':
                // prevent modifier keys from resetting the suggestion state
                break;
            // Otherwise, check if a mention is typed
            default:
                this.saveStateInStore();
        }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(ComposerTextInput, {
<<<<<<< HEAD
    props: { record: Object },
=======
    components,
    defaultProps: {
        hasMentionSuggestionsBelowPosition: false,
        sendShortcuts: [],
    },
    props: {
        composerLocalId: String,
        hasMentionSuggestionsBelowPosition: Boolean,
        isCompact: Boolean,
        /**
         * Keyboard shortcuts from text input to send message.
         */
        sendShortcuts: {
            type: Array,
            element: String,
            validate: prop => {
                for (const shortcut of prop) {
                    if (!['ctrl-enter', 'enter', 'meta-enter'].includes(shortcut)) {
                        return false;
                    }
                }
                return true;
            },
        },
    },
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    template: 'mail.ComposerTextInput',
});

registerMessagingComponent(ComposerTextInput);
