/** @odoo-module **/

<<<<<<< HEAD
import { useUpdateToModel } from '@mail/component_hooks/use_update_to_model';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    Dialog: require('mail/static/src/components/dialog/dialog.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

export class DialogManager extends Component {

    /**
     * @override
     */
<<<<<<< HEAD
    setup() {
        super.setup();
        useUpdateToModel({ methodName: 'onComponentUpdate' });
=======
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const dialogManager = this.env.messaging && this.env.messaging.dialogManager;
            return {
                dialogManager: dialogManager ? dialogManager.__state : undefined,
            };
        });
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    get dialogManager() {
        return this.props.record;
    }
<<<<<<< HEAD
=======

    patched() {
        this._checkDialogOpen();
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _checkDialogOpen() {
        if (!this.env.messaging) {
            /**
             * Messaging not created, which means essential models like
             * dialog manager are not ready, so open status of dialog in DOM
             * is omitted during this (short) period of time.
             */
            return;
        }
        if (this.env.messaging.dialogManager.dialogs.length > 0) {
            document.body.classList.add('modal-open');
        } else {
            document.body.classList.remove('modal-open');
        }
    }

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
}

Object.assign(DialogManager, {
    props: { record: Object },
    template: 'mail.DialogManager',
});

registerMessagingComponent(DialogManager);
