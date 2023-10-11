/** @odoo-module **/

<<<<<<< HEAD
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');

const { Component, useState } = owl;
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

<<<<<<< HEAD
export class DropZone extends Component {
=======
    /**
     * @override
     */
    constructor(...args) {
        super(...args);
        useShouldUpdateBasedOnProps();
        this.state = useState({
            /**
             * Determine whether the user is dragging files over the dropzone.
             * Useful to provide visual feedback in that case.
             */
            isDraggingInside: false,
        });
        /**
         * Counts how many drag enter/leave happened on self and children. This
         * ensures the drop effect stays active when dragging over a child.
         */
        this._dragCount = 0;
    }
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {DropZoneView}
     */
    get dropZoneView() {
        return this.props.record;
    }

    /**
     * Returns whether the given node is self or a children of self.
     *
     * @param {Node} node
     * @returns {boolean}
     */
    contains(node) {
        return Boolean(this.root.el && this.root.el.contains(node));
    }

}

Object.assign(DropZone, {
    props: {
        record: Object,
        onDropzoneFilesDropped: {
            type: Function,
            optional: true,
        },
    },
    template: 'mail.DropZone',
});

registerMessagingComponent(DropZone);
