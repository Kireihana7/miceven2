odoo.define("website.tour.snippet_empty_parent_autoremove", function (require) {
"use strict";

<<<<<<< HEAD
=======
const tour = require('web_tour.tour');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
const wTourUtils = require('website.tour_utils');

function removeSelectedBlock() {
    return {
        content: "Remove selected block",
<<<<<<< HEAD
        trigger: '#oe_snippets we-customizeblock-options:nth-last-child(3) .oe_snippet_remove',
    };
}

wTourUtils.registerWebsitePreviewTour('snippet_empty_parent_autoremove', {
    test: true,
    url: '/',
    edition: true,
=======
        trigger: '#oe_snippets we-customizeblock-options:last-child .oe_snippet_remove',
    };
}

tour.register('snippet_empty_parent_autoremove', {
    test: true,
    url: '/?enable_editor=1',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
}, [
    // Base case: remove both columns from text - image
    wTourUtils.dragNDrop({
        id: 's_text_image',
        name: 'Text - Image',
    }),
    {
        content: "Click on second column",
<<<<<<< HEAD
        trigger: 'iframe #wrap .s_text_image .row > :nth-child(2)',
=======
        trigger: '#wrap .s_text_image .row > :nth-child(2)',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    removeSelectedBlock(),
    {
        content: "Click on first column",
<<<<<<< HEAD
        trigger: 'iframe #wrap .s_text_image .row > :first-child',
=======
        trigger: '#wrap .s_text_image .row > :first-child',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    removeSelectedBlock(),
    {
        content: "Check that #wrap is empty",
<<<<<<< HEAD
        trigger: 'iframe #wrap:empty',
=======
        trigger: '#wrap:empty',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },

    // Banner: test that parallax, bg-filter and shape are not treated as content
    wTourUtils.dragNDrop({
        id: 's_banner',
        name: 'Banner',
    }),
    wTourUtils.clickOnSnippet({
        id: 's_banner',
        name: 'Banner',
    }),
    {
        content: "Check that parallax is present",
<<<<<<< HEAD
        trigger: 'iframe #wrap .s_banner .s_parallax_bg',
=======
        trigger: '#wrap .s_banner .s_parallax_bg',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        run: () => null,
    },
    wTourUtils.changeOption('ColoredLevelBackground', 'Shape'),
    {
        content: "Check that shape is present",
<<<<<<< HEAD
        trigger: 'iframe #wrap .s_banner .o_we_shape',
=======
        trigger: '#wrap .s_banner .o_we_shape',
        run: () => null,
    },
    wTourUtils.changeOption('ColoredLevelBackground', 'Filter'),
    {
        content: "Check that background-filter is present",
        trigger: '#wrap .s_banner .o_we_bg_filter',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        run: () => null,
    },
    {
        content: "Click on first column",
<<<<<<< HEAD
        trigger: 'iframe #wrap .s_banner .row > :first-child',
=======
        trigger: '#wrap .s_banner .row > :first-child',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    removeSelectedBlock(),
    {
        content: "Check that #wrap is empty",
<<<<<<< HEAD
        trigger: 'iframe #wrap:empty',
=======
        trigger: '#wrap:empty',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        run: () => null,
    },
]);
});
