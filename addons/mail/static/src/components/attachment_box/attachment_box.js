/** @odoo-module **/

<<<<<<< HEAD
import { useComponentToModel } from '@mail/component_hooks/use_component_to_model';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
=======
const components = {
    AttachmentList: require('mail/static/src/components/attachment_list/attachment_list.js'),
    DropZone: require('mail/static/src/components/drop_zone/drop_zone.js'),
    FileUploader: require('mail/static/src/components/file_uploader/file_uploader.js'),
};
const useDragVisibleDropZone = require('mail/static/src/component_hooks/use_drag_visible_dropzone/use_drag_visible_dropzone.js');
const useShouldUpdateBasedOnProps = require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
const useStore = require('mail/static/src/component_hooks/use_store/use_store.js');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

const { Component } = owl;

export class AttachmentBox extends Component {

    /**
     * @override
     */
<<<<<<< HEAD
    setup() {
        super.setup();
        useComponentToModel({ fieldName: 'component' });
=======
    constructor(...args) {
        super(...args);
        this.isDropZoneVisible = useDragVisibleDropZone();
        useShouldUpdateBasedOnProps();
        useStore(props => {
            const thread = this.env.models['mail.thread'].get(props.threadLocalId);
            return {
                thread,
                threadAllAttachments: thread ? thread.allAttachments : [],
                threadId: thread && thread.id,
                threadModel: thread && thread.model,
            };
        }, {
            compareDepth: {
                threadAllAttachments: 1,
            },
        });
        /**
         * Reference of the file uploader.
         * Useful to programmatically prompts the browser file uploader.
         */
        this._fileUploaderRef = useRef('fileUploader');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {AttachmentBoxView|undefined}
     */
    get attachmentBoxView() {
        return this.props.record;
    }

}

Object.assign(AttachmentBox, {
    props: { record: Object },
    template: 'mail.AttachmentBox',
});

registerMessagingComponent(AttachmentBox);
