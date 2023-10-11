/** @odoo-module **/

<<<<<<< HEAD
import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class MailTemplate extends Component {
=======
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');

const { Component } = owl;

class MailTemplate extends Component {

    /**
     * @override
     */
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const activity = this.env.models['mail.activity'].get(props.activityLocalId);
            const mailTemplate = this.env.models['mail.mail_template'].get(props.mailTemplateLocalId);
            return {
                activity: activity ? activity.__state : undefined,
                mailTemplate: mailTemplate ? mailTemplate.__state : undefined,
            };
        });
    }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {MailTemplateView}
     */
    get mailTemplateView() {
        return this.props.record;
    }

}

Object.assign(MailTemplate, {
    props: { record: Object },
    template: 'mail.MailTemplate',
});

registerMessagingComponent(MailTemplate);
