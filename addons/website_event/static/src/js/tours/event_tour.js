odoo.define('website_event.event_steps', function (require) {
"use strict";

const {_t} = require('web.core');
const {Markup} = require('web.utils');

var EventAdditionalTourSteps = require('event.event_steps');

EventAdditionalTourSteps.include({

    init: function() {
        this._super.apply(this, arguments);
    },

    _get_website_event_steps: function () {
        this._super.apply(this, arguments);
        return [{
<<<<<<< HEAD
                trigger: '.o_event_form_view button[title="Unpublished"]',
                content: Markup(_t("Use this <b>shortcut</b> to easily access your event web page.")),
                position: 'bottom',
            }, {
                trigger: '.o_edit_website_container a',
                content: Markup(_t("With the Edit button, you can <b>customize</b> the web page visitors will see when registering.")),
                position: 'bottom',
            }, {
                trigger: '#oe_snippets.o_loaded div[name="Image - Text"] .oe_snippet_thumbnail',
                content: Markup(_t("<b>Drag and Drop</b> this snippet below the event title.")),
=======
                trigger: '.o_event_form_view button[name="is_published"]',
                content: _t("Use this <b>shortcut</b> to easily access your event web page."),
                position: 'bottom',
            }, {
                trigger: 'li#edit-page-menu a',
                extra_trigger: '.o_wevent_event',
                content: _t("With the Edit button, you can <b>customize</b> the web page visitors will see when registering."),
                position: 'bottom',
            }, {
                trigger: 'div[name="Image - Text"] .oe_snippet_thumbnail',
                extra_trigger: '.o_wevent_event',
                content: _t("<b>Drag and Drop</b> this snippet below the event title."),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                position: 'bottom',
                run: 'drag_and_drop iframe #o_wevent_event_main_col',
            }, {
                trigger: 'button[data-action="save"]',
<<<<<<< HEAD
                content: Markup(_t("Don't forget to click <b>save</b> when you're done.")),
                position: 'bottom',
            }, {
                trigger: '.o_menu_systray_item .o_switch_danger_success',
                extra_trigger: 'iframe body:not(.editor_enable) .o_wevent_event',
                content: Markup(_t("Looking great! Let's now <b>publish</b> this page so that it becomes <b>visible</b> on your website!")),
                position: 'bottom',
            }, {
                trigger: '.o_website_edit_in_backend > a',
                extra_trigger: 'iframe .o_wevent_event',
=======
                extra_trigger: '.o_wevent_event',
                content: _t("Don't forget to click <b>save</b> when you're done."),
                position: 'bottom',
            }, {
                trigger: 'label.js_publish_btn',
                extra_trigger: '.o_wevent_event',
                content: _t("Looking great! Let's now <b>publish</b> this page so that it becomes <b>visible</b> on your website!"),
                position: 'bottom',
            }, {
                trigger: 'a.css_edit_dynamic',
                extra_trigger: '.js_publish_management[data-object="event.event"] .js_publish_btn .css_unpublish:visible',
                content: _t("Want to change your event configuration? Let's go back to the event form."),
                position: 'bottom',
                run: function (actions) {
                    actions.click('div.dropdown-menu a#edit-in-backend');
                },
            }, {
                trigger: 'a#edit-in-backend',
                extra_trigger: '.o_wevent_event',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                content: _t("This shortcut will bring you right back to the event form."),
                position: 'bottom'
            }];
    }
});

return EventAdditionalTourSteps;

});
