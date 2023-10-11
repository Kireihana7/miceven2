<<<<<<< HEAD
/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class ComposerSuggestedRecipientList extends Component {
=======
odoo.define('mail/static/src/components/composer_suggested_recipient_list/composer_suggested_recipient_list.js', function (require) {
'use strict';

const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');

const { Component } = owl;
const { useState } = owl.hooks;

const components = {
    ComposerSuggestedRecipient: require('mail/static/src/components/composer_suggested_recipient/composer_suggested_recipient.js'),
};

class ComposerSuggestedRecipientList extends Component {

    /**
     * @override
     */
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        this.state = useState({
            hasShowMoreButton: false,
        });
        useStore(props => {
            const thread = this.env.models['mail.thread'].get(props.threadLocalId);
            return {
                threadSuggestedRecipientInfoList: thread ? thread.suggestedRecipientInfoList : [],
            };
        }, {
            compareDepth: {
                threadSuggestedRecipientInfoList: 1,
            },
        });
    }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
<<<<<<< HEAD
     * @returns {ComposerSuggestedRecipientListView}
     */
    get composerSuggestedRecipientListView() {
        return this.props.record;
=======
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
     */
    _onClickShowLess(ev) {
        this.state.hasShowMoreButton = false;
    }

    /**
     * @private
     */
    _onClickShowMore(ev) {
        this.state.hasShowMoreButton = true;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

}

Object.assign(ComposerSuggestedRecipientList, {
<<<<<<< HEAD
    props: { record: Object },
    template: 'mail.ComposerSuggestedRecipientList',
});

registerMessagingComponent(ComposerSuggestedRecipientList);
=======
    components,
    props: {
        threadLocalId: String,
    },
    template: 'mail.ComposerSuggestedRecipientList',
});

return ComposerSuggestedRecipientList;
});
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
