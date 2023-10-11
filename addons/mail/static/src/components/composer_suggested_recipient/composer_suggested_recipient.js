<<<<<<< HEAD
/** @odoo-module **/

import { useUpdate } from '@mail/component_hooks/use_update';
import { registerMessagingComponent } from '@mail/utils/messaging_component';

import { useService } from "@web/core/utils/hooks";
import { FormViewDialog } from '@web/views/view_dialogs/form_view_dialog';

const { Component, useRef } = owl;

export class ComposerSuggestedRecipient extends Component {

    /**
     * @override
     */
    setup() {
        super.setup();
        this.id = _.uniqueId('o_ComposerSuggestedRecipient_');
        useUpdate({ func: () => this._update() });
        /**
=======
odoo.define('mail/static/src/components/composer_suggested_recipient/composer_suggested_recipient.js', function (require) {
'use strict';

const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
const useUpdate = require('mail/static/src/component_hooks/use_update/use_update.js');

const { FormViewDialog } = require('web.view_dialogs');
const { ComponentAdapter } = require('web.OwlCompatibility');
const session = require('web.session');

const { Component } = owl;
const { useRef } = owl.hooks;

class FormViewDialogComponentAdapter extends ComponentAdapter {

    renderWidget() {
        // Ensure the dialog is properly reconstructed. Without this line, it is
        // impossible to open the dialog again after having it closed a first
        // time, because the DOM of the dialog has disappeared.
        return this.willStart();
    }

}

const components = {
    FormViewDialogComponentAdapter,
};

class ComposerSuggestedRecipient extends Component {

    constructor(...args) {
        super(...args);
        this.id = _.uniqueId('o_ComposerSuggestedRecipient_');
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const suggestedRecipientInfo = this.env.models['mail.suggested_recipient_info'].get(props.suggestedRecipientLocalId);
            const partner = suggestedRecipientInfo && suggestedRecipientInfo.partner;
            return {
                partner: partner && partner.__state,
                suggestedRecipientInfo: suggestedRecipientInfo && suggestedRecipientInfo.__state,
            };
        });
        useUpdate({ func: () => this._update() });
        /**
         * Form view dialog class. Useful to reference it in the template.
         */
        this.FormViewDialog = FormViewDialog;
        /**
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
         * Reference of the checkbox. Useful to know whether it was checked or
         * not, to properly update the corresponding state in the record or to
         * prompt the user with the partner creation dialog.
         */
        this._checkboxRef = useRef('checkbox');
<<<<<<< HEAD
        this.dialogService = useService("dialog");
=======
        /**
         * Reference of the partner creation dialog. Useful to open it, for
         * compatibility with old code.
         */
        this._dialogRef = useRef('dialog');
        /**
         * Whether the dialog is currently open. `_dialogRef` cannot be trusted
         * to know if the dialog is open due to manually calling `open` and
         * potential out of sync with component adapter.
         */
        this._isDialogOpen = false;
        this._onDialogSaved = this._onDialogSaved.bind(this);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
<<<<<<< HEAD
     * @returns {ComposerSuggestedRecipientView}
     */
    get composerSuggestedRecipientView() {
        return this.props.record;
=======
     * @returns {string|undefined}
     */
    get ADD_AS_RECIPIENT_AND_FOLLOWER_REASON() {
        if (!this.suggestedRecipientInfo) {
            return undefined;
        }
        return this.env._t(_.str.sprintf(
            "Add as recipient and follower (reason: %s)",
            this.suggestedRecipientInfo.reason
        ));
    }

    /**
     * @returns {string}
     */
    get PLEASE_COMPLETE_CUSTOMER_S_INFORMATION() {
        return this.env._t("Please complete customer's information");
    }

    /**
     * @returns {mail.suggested_recipient_info}
     */
    get suggestedRecipientInfo() {
        return this.env.models['mail.suggested_recipient_info'].get(this.props.suggestedRecipientInfoLocalId);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _update() {
<<<<<<< HEAD
        if (this._checkboxRef.el && this.composerSuggestedRecipientView.suggestedRecipientInfo) {
            this._checkboxRef.el.checked = this.composerSuggestedRecipientView.suggestedRecipientInfo.isSelected;
=======
        if (this._checkboxRef.el && this.suggestedRecipientInfo) {
            this._checkboxRef.el.checked = this.suggestedRecipientInfo.isSelected;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
    }

    //--------------------------------------------------------------------------
    // Handler
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onChangeCheckbox() {
<<<<<<< HEAD
        if (!this.composerSuggestedRecipientView.exists()) {
            return;
        }
        const isChecked = this._checkboxRef.el.checked;
        this.composerSuggestedRecipientView.suggestedRecipientInfo.update({ isChecked });
        if (!this.composerSuggestedRecipientView.suggestedRecipientInfo.partner) {
            // Recipients must always be partners. On selecting a suggested
            // recipient that does not have a partner, the partner creation form
            // should be opened.
            if (isChecked) {
                this.dialogService.add(FormViewDialog, {
                    context: {
                        active_id: this.composerSuggestedRecipientView.suggestedRecipientInfo.thread.id,
                        active_model: 'mail.compose.message',
                        default_email: this.composerSuggestedRecipientView.suggestedRecipientInfo.email,
                        default_name: this.composerSuggestedRecipientView.suggestedRecipientInfo.name,
                        default_lang: this.composerSuggestedRecipientView.suggestedRecipientInfo.lang,
                        force_email: true,
                        ref: 'compound_context',
                    },
                    onRecordSaved: () => this._onDialogSaved(),
                    resModel: "res.partner",
                    title: this.composerSuggestedRecipientView.suggestedRecipientInfo.dialogText,
                }, {
                    onClose: () => {
                        this._checkboxRef.el.checked = !!this.composerSuggestedRecipientView.suggestedRecipientInfo.partner;
                    },
                });
=======
        const isChecked = this._checkboxRef.el.checked;
        this.suggestedRecipientInfo.update({ isSelected: isChecked });
        if (!this.suggestedRecipientInfo.partner) {
            // Recipients must always be partners. On selecting a suggested
            // recipient that does not have a partner, the partner creation form
            // should be opened.
            if (isChecked && this._dialogRef && !this._isDialogOpen) {
                const widget = this._dialogRef.comp.widget;
                this._isDialogOpen = true;
                widget.on('closed', this, () => {
                    this._isDialogOpen = false;
                    this._checkboxRef.el.checked = !!this.suggestedRecipientInfo.partner;
                });
                widget.context = Object.assign({}, widget.context, session.user_context)
                widget.open();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }
        }
    }

    /**
     * @private
     */
    _onDialogSaved() {
<<<<<<< HEAD
        if (!this.composerSuggestedRecipientView.exists()) {
            return;
        }
        const thread = (
            this.composerSuggestedRecipientView.suggestedRecipientInfo &&
            this.composerSuggestedRecipientView.suggestedRecipientInfo.thread
        );
        if (!thread) {
            return;
        }
        thread.fetchData(['suggestedRecipients']);
=======
        const thread = this.suggestedRecipientInfo && this.suggestedRecipientInfo.thread;
        if (!thread) {
            return;
        }
        thread.fetchAndUpdateSuggestedRecipients();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }
}

Object.assign(ComposerSuggestedRecipient, {
<<<<<<< HEAD
    props: { record: Object },
    template: 'mail.ComposerSuggestedRecipient',
});

registerMessagingComponent(ComposerSuggestedRecipient);
=======
    components,
    props: {
        suggestedRecipientInfoLocalId: String,
    },
    template: 'mail.ComposerSuggestedRecipient',
});

return ComposerSuggestedRecipient;

});
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
