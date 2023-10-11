/** @odoo-module **/

<<<<<<< HEAD
import { useModels } from '@mail/component_hooks/use_models';
// ensure components are registered beforehand.
import '@mail/components/chatter/chatter';
import { clear } from '@mail/model/model_field_command';
import { getMessagingComponent } from "@mail/utils/messaging_component";
=======
const components = {
    Chatter: require('mail/static/src/components/chatter/chatter.js'),
};
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
const useUpdate = require('mail/static/src/component_hooks/use_update/use_update.js');
const { clear } = require('mail/static/src/model/model_field_command.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component, onWillDestroy, onWillUpdateProps } = owl;

export const getChatterNextTemporaryId = (function () {
    let tmpId = 0;
    return () => {
        tmpId += 1;
        return tmpId;
    };
})();

/**
 * This component abstracts chatter component to its parent, so that it can be
 * mounted and receive chatter data even when a chatter component cannot be
 * created. Indeed, in order to create a chatter component, we must create
 * a chatter record, the latter requiring messaging to be initialized. The view
 * may attempt to create a chatter before messaging has been initialized, so
 * this component delays the mounting of chatter until it becomes initialized.
 */
export class ChatterContainer extends Component {

    /**
     * @override
     */
<<<<<<< HEAD
    setup() {
        useModels();
        super.setup();
        this.localChatter = undefined;
        this._insertFromProps(this.props);
        onWillUpdateProps(nextProps => {
            this._insertFromProps(nextProps);
        });
        onWillDestroy(() => this.deleteLocalChatter());
    }

    get chatter() {
        return this.props.chatter || this.localChatter;
    }

    deleteLocalChatter() {
        if (this.localChatter && this.localChatter.exists()) {
            this.localChatter.delete();
=======
    constructor(...args) {
        super(...args);
        this.chatter = undefined;
        this._wasMessagingInitialized = false;
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const isMessagingInitialized = this.env.isMessagingInitialized();
            // Delay creation of chatter record until messaging is initialized.
            // Ideally should observe models directly to detect change instead
            // of using `useStore`.
            if (!this._wasMessagingInitialized && isMessagingInitialized) {
                this._wasMessagingInitialized = true;
                this._insertFromProps(props);
            }
            return { chatter: this.chatter };
        });
        useUpdate({ func: () => this._update() });
    }

    /**
     * @override
     */
    willUpdateProps(nextProps) {
        if (this.env.isMessagingInitialized()) {
            this._insertFromProps(nextProps);
        }
        return super.willUpdateProps(...arguments);
    }

    /**
     * @override
     */
    destroy() {
        super.destroy();
        if (this.chatter) {
            this.chatter.delete();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
<<<<<<< HEAD
    async _insertFromProps(props) {
        const messaging = await this.env.services.messaging.get();
        if (owl.status(this) === "destroyed") {
            return;
=======
    _insertFromProps(props) {
        const values = Object.assign({}, props);
        if (values.threadId === undefined) {
            values.threadId = clear();
        }
        if (!this.chatter) {
            this.chatter = this.env.models['mail.chatter'].create(values);
        } else {
            this.chatter.update(values);
        }
    }

    /**
     * @private
     */
    _update() {
        if (this.chatter) {
            this.chatter.refresh();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        }
        const values = { ...props };
        delete values.chatter;
        delete values.className;
        if (values.threadId === undefined) {
            values.threadId = clear();
        }
        const hasToCreateChatter = !props.chatter && !this.localChatter;
        if (hasToCreateChatter) {
            this.localChatter = messaging.models['Chatter'].insert({ id: getChatterNextTemporaryId(), ...values });
        }
        const chatter = props.chatter || this.localChatter;
        if (!hasToCreateChatter) {
            chatter.update(values);
        }
        if (owl.status(this) === "destroyed") {
            // insert might trigger a re-render which might destroy the current component
            this.deleteLocalChatter();
            return;
        }
        /**
         * Refresh the chatter when the parent view is (re)loaded.
         * This serves mainly at loading initial data, but also on reload there
         * might be new message, new attachment, ...
         *
         * For example in approvals this is currently necessary to fetch the
         * newly added attachment when using the "Attach Document" button. And
         * in sales it is necessary to see the email when using the "Send email"
         * button.
         *
         * NOTE: this assumes props are actually changed when a reload of parent
         * happens which is true so far because of the OWL compatibility layer
         * calling the props change method but it is in general not a good
         * assumption to make.
         */
        if (chatter.thread) {
            chatter.refresh();
        }
        this.render();
    }

}

Object.assign(ChatterContainer, {
<<<<<<< HEAD
    components: { Chatter: getMessagingComponent('Chatter') },
    props: {
        chatter: {
            type: Object,
            optional: true,
        },
        className: {
            type: String,
            optional: true,
        },
=======
    components,
    props: {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        hasActivities: {
            type: Boolean,
            optional: true,
        },
        hasExternalBorder: {
            type: Boolean,
            optional: true,
        },
        hasFollowers: {
            type: Boolean,
            optional: true,
        },
        hasMessageList: {
            type: Boolean,
            optional: true,
        },
        hasMessageListScrollAdjust: {
            type: Boolean,
            optional: true,
        },
<<<<<<< HEAD
        hasParentReloadOnAttachmentsChanged: {
            type: Boolean,
            optional: true,
        },
        hasParentReloadOnFollowersUpdate: {
            type: Boolean,
            optional: true,
        },
        hasParentReloadOnMessagePosted: {
            type: Boolean,
            optional: true,
        },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        hasTopbarCloseButton: {
            type: Boolean,
            optional: true,
        },
        isAttachmentBoxVisibleInitially: {
            type: Boolean,
            optional: true,
        },
<<<<<<< HEAD
        isInFormSheetBg: {
            type: Boolean,
            optional: true,
        },
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        threadId: {
            type: Number,
            optional: true,
        },
        threadModel: String,
<<<<<<< HEAD
        webRecord: {
            type: Object,
            optional: true,
        },
        saveRecord: {
            type: Function,
            optional: true,
        }
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    template: 'mail.ChatterContainer',
});
