/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');

const { Component } = owl;

<<<<<<< HEAD
export class ThreadTypingIcon extends Component {}
=======
class ThreadTypingIcon extends Component {

    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
    }

}
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

Object.assign(ThreadTypingIcon, {
    defaultProps: {
        animation: 'none',
        size: 'small',
    },
    props: {
        animation: {
            type: String,
            validate: prop => ['bounce', 'none', 'pulse'].includes(prop),
            optional: true,
        },
        size: {
            type: String,
            validate: prop => ['small', 'medium'].includes(prop),
            optional: true,
        },
        title: {
            type: String,
            optional: true,
        }
    },
    template: 'mail.ThreadTypingIcon',
});

registerMessagingComponent(ThreadTypingIcon);
