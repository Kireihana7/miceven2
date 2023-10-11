/** @odoo-module **/

<<<<<<< HEAD
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const patchMixin = require('web.patchMixin');

const { Component } = owl;

<<<<<<< HEAD
export class Dialog extends Component {
=======
class Dialog extends Component {

    /**
     * @param {...any} args
     */
    constructor(...args) {
        super(...args);
        /**
         * Reference to the component used inside this dialog.
         */
        this._componentRef = useRef('component');
        this._onClickGlobal = this._onClickGlobal.bind(this);
        this._onKeydownDocument = this._onKeydownDocument.bind(this);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const dialog = this.env.models['mail.dialog'].get(props.dialogLocalId);
            return {
                dialog: dialog ? dialog.__state : undefined,
            };
        });
        this._constructor();
    }

    /**
     * Allows patching constructor.
     */
    _constructor() {}

    mounted() {
        document.addEventListener('click', this._onClickGlobal, true);
        document.addEventListener('keydown', this._onKeydownDocument);
    }

    willUnmount() {
        document.removeEventListener('click', this._onClickGlobal, true);
        document.removeEventListener('keydown', this._onKeydownDocument);
    }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {Dialog}
     */
    get dialog() {
        return this.props.record;
    }

}

Object.assign(Dialog, {
    props: { record: Object },
    template: 'mail.Dialog',
});

<<<<<<< HEAD
registerMessagingComponent(Dialog);
=======
return patchMixin(Dialog);

});
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
