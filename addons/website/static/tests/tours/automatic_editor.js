odoo.define('website.tour.automatic_editor', function (require) {
'use strict';

<<<<<<< HEAD
const wTourUtils = require("website.tour_utils");

wTourUtils.registerWebsitePreviewTour('automatic_editor_on_new_website', {
=======
const tour = require('web_tour.tour');

tour.register('automatic_editor_on_new_website', {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    test: true,
    url: '/',
},
[
    {
        content: "Select the language dropdown",
<<<<<<< HEAD
        trigger: 'iframe .js_language_selector .dropdown-toggle'
    },
    {
        content: "click on Add a language",
        trigger: 'iframe a.o_add_language',
    },
    {
        content: "type Parseltongue",
        trigger: 'div[name="lang_ids"] .o_input_dropdown input',
        run: 'text Parseltongue',
    },
    {
        content: 'select Parseltongue',
        trigger: '.dropdown-item:contains(Parseltongue)',
        in_modal: false,
    },
    {
        content: "load parseltongue",
        extra_trigger: '.modal div[name="lang_ids"] .rounded-pill .o_tag_badge_text:contains(Parseltongue)',
        trigger: '.modal-footer button[name=lang_install]',
    },
    {
        content: "Select the language dropdown",
        trigger: 'iframe .js_language_selector .dropdown-toggle',
    },
    {
        content: "Select parseltongue",
        trigger: 'iframe a.js_change_lang[data-url_code=pa_GB]',
        extra_trigger: 'iframe a.js_change_lang .o_lang_flag',
    },
    {
        content: "Check that we're on parseltongue and then go to settings",
        trigger: 'iframe html[lang=pa-GB]',
=======
        trigger: '.js_language_selector .dropdown-toggle'
    },
    {
        content: "click on Add a language",
        trigger: 'a.o_add_language',
    },
    {
        content: "Select dropdown",
        trigger: 'select[name=lang]',
        run: () => {
            $('select[name="lang"]').val('"pa_GB"').change();
        }
    },
    {
        content: "load parseltongue",
        extra_trigger: '.modal select[name="lang"]:propValueContains(pa_GB)',
        trigger: '.modal-footer button:first',
    },
    {
        content: "Select the language dropdown",
        trigger: '.js_language_selector .dropdown-toggle',
    },
    {
        content: "Select parseltongue",
        trigger: 'a.js_change_lang[data-url_code=pa_GB]',
    },
    {
        content: "Check that we're on parseltongue and then go to settings",
        trigger: 'html[lang=pa-GB]',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        run: () => {
            // Now go through the settings for a new website. A frontend_lang
            // cookie was set during previous steps. It should not be used when
            // redirecting to the frontend in the following steps.
            window.location.href = '/web#action=website.action_website_configuration';
        }
    },
    {
        content: "create a new website",
        trigger: 'button[name="action_website_create_new"]',
    },
    {
        content: "insert website name",
<<<<<<< HEAD
        trigger: 'div[name="name"] input',
=======
        trigger: 'input[name="name"]',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        run: 'text Website EN'
    },
    {
        content: "validate the website creation modal",
        trigger: 'button.btn-primary'
    },
    {
<<<<<<< HEAD
        content: "skip configurator",
        // This trigger targets the skip button, it doesn't have a more
        // explicit class or ID.
        trigger: '.o_configurator_container .container-fluid .btn.btn-link'
    },
    {
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        content: "make hover button appear",
        trigger: '.o_theme_preview',
        run: () => {
            $('.o_theme_preview .o_button_area').attr('style', 'visibility: visible; opacity: 1;');
        },
    },
    {
        content: "Install a theme",
<<<<<<< HEAD
        trigger: 'button[name="button_choose_theme"]'
    },
    {
        content: "Check that the editor is loaded",
        trigger: 'iframe body.editor_enable',
=======
        trigger: 'button[data-name="button_choose_theme"]'
    },
    {
        content: "Check that the editor is loaded",
        trigger: 'body.editor_enable',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        timeout: 30000,
        run: () => null, // it's a check
    },
    {
        content: "exit edit mode",
        trigger: '.o_we_website_top_actions button.btn-primary:contains("Save")',
    },
    {
        content: "wait for editor to close",
<<<<<<< HEAD
        trigger: 'iframe body:not(.editor_enable)',
=======
        trigger: 'body:not(.editor_enable)',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        run: () => null, // It's a check
    }
]);
});
