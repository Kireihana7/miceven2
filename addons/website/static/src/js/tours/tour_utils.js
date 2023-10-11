odoo.define("website.tour_utils", function (require) {
"use strict";

<<<<<<< HEAD
const {_t} = require("web.core");
const {Markup} = require('web.utils');
var tour = require("web_tour.tour");

function addMedia(position = "right") {
    return {
        trigger: `.modal-content footer .btn-primary`,
        content: Markup(_t("<b>Add</b> the selected image.")),
=======
const core = require("web.core");
const _t = core._t;

var tour = require("web_tour.tour");

/**

const snippets = [
    {
        id: 's_cover',
        name: 'Cover',
    },
    {
        id: 's_text_image',
        name: 'Text - Image',
    }
];

tour.register("themename_tour", {
    url: "/",
    saveAs: "homepage",
}, [
    wTourUtils.dragNDrop(snippets[0]),
    wTourUtils.clickOnText(snippets[0], 'h1'),
    wTourUtils.changeOption('colorFilter', 'span.o_we_color_preview', _t('color filter')),
    wTourUtils.selectHeader(),
    wTourUtils.changeOption('HeaderTemplate', '[data-name="header_alignment_opt"]', _t('alignment')),
    wTourUtils.goBackToBlocks(),
    wTourUtils.dragNDrop(snippets[1]),
    wTourUtils.changeImage(snippets[1]),
    wTourUtils.clickOnSave(),
]);
**/



function addMedia(position = "right") {
    return {
        trigger: `.modal-content footer .btn-primary`,
        content: _t("<b>Add</b> the selected image."),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: "click",
    };
}
<<<<<<< HEAD
function assertCssVariable(variableName, variableValue, trigger = 'iframe body') {
    return {
        content: `Check CSS variable ${variableName}=${variableValue}`,
        trigger: trigger,
        auto: true,
        run: function () {
            const styleValue = getComputedStyle(this.$anchor[0]).getPropertyValue(variableName);
            if ((styleValue && styleValue.trim().replace(/["']/g, '')) !== variableValue.trim().replace(/["']/g, '')) {
                throw new Error(`Failed precondition: ${variableName}=${styleValue} (should be ${variableValue})`);
            }
        },
    };
}
function assertPathName(pathName, trigger) {
    return {
        content: `Check if we have been redirected to ${pathName}`,
        trigger: trigger,
        run: () => {
            if (!window.location.pathname.startsWith(pathName)) {
                console.error(`We should be on ${pathName}.`);
            }
        }
    };
}

function changeBackground(snippet, position = "bottom") {
    return {
        trigger: ".o_we_customize_panel .o_we_bg_success",
        content: Markup(_t("<b>Customize</b> any block through this menu. Try to change the background image of this block.")),
=======

function changeBackground(snippet, position = "bottom") {
    return {
        trigger: ".o_we_customize_panel .o_we_edit_image",
        content: _t("<b>Customize</b> any block through this menu. Try to change the background image of this block."),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: "click",
    };
}

function changeBackgroundColor(position = "bottom") {
    return {
        trigger: ".o_we_customize_panel .o_we_color_preview",
<<<<<<< HEAD
        content: Markup(_t("<b>Customize</b> any block through this menu. Try to change the background color of this block.")),
=======
        content: _t("<b>Customize</b> any block through this menu. Try to change the background color of this block."),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: "click",
    };
}

function selectColorPalette(position = "left") {
    return {
        trigger: ".o_we_customize_panel .o_we_so_color_palette we-selection-items",
        alt_trigger: ".o_we_customize_panel .o_we_color_preview",
<<<<<<< HEAD
        content: Markup(_t(`<b>Select</b> a Color Palette.`)),
=======
        content: _t(`<b>Select</b> a Color Palette.`),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: 'click',
        location: position === 'left' ? '#oe_snippets' : undefined,
    };
}

function changeColumnSize(position = "right") {
    return {
<<<<<<< HEAD
        trigger: `iframe .oe_overlay.ui-draggable.o_we_overlay_sticky.oe_active .o_handle.e`,
        content: Markup(_t("<b>Slide</b> this button to change the column size.")),
=======
        trigger: `.oe_overlay.ui-draggable.o_we_overlay_sticky.oe_active .o_handle.e`,
        content: _t("<b>Slide</b> this button to change the column size."),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
    };
}

function changeIcon(snippet, index = 0, position = "bottom") {
    return {
        trigger: `#wrapwrap .${snippet.id} i:eq(${index})`,
<<<<<<< HEAD
        extra_trigger: "body.editor_enable",
        content: Markup(_t("<b>Double click on an icon</b> to change it with one of your choice.")),
=======
        content: _t("<b>Double click on an icon</b> to change it with one of your choice."),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: "dblclick",
    };
}

function changeImage(snippet, position = "bottom") {
    return {
<<<<<<< HEAD
        trigger: snippet.id ? `#wrapwrap .${snippet.id} img` : snippet,
        extra_trigger: "body.editor_enable",
        content: Markup(_t("<b>Double click on an image</b> to change it with one of your choice.")),
=======
        trigger: `#wrapwrap .${snippet.id} img`,
        content: _t("<b>Double click on an image</b> to change it with one of your choice."),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: "dblclick",
    };
}

/**
    wTourUtils.changeOption('HeaderTemplate', '[data-name="header_alignment_opt"]', _t('alignment')),
<<<<<<< HEAD
    By default, prevents the step from being active if a palette is opened.
    Set allowPalette to true to select options within a palette.
*/
function changeOption(optionName, weName = '', optionTooltipLabel = '', position = "bottom", allowPalette = false) {
    const noPalette = allowPalette ? '' : '.o_we_customize_panel:not(:has(.o_we_so_color_palette.o_we_widget_opened))';
    const option_block = `${noPalette} we-customizeblock-option[class='snippet-option-${optionName}']`;
    return {
        trigger: `${option_block} ${weName}, ${option_block} [title='${weName}']`,
        content: Markup(_.str.sprintf(_t("<b>Click</b> on this option to change the %s of the block."), optionTooltipLabel)),
=======
*/
function changeOption(optionName, weName = '', optionTooltipLabel = '', position = "bottom") {
    const option_block = `we-customizeblock-option[class='snippet-option-${optionName}']`
    return {
        trigger: `${option_block} ${weName}, ${option_block} [title='${weName}']`,
        content: _.str.sprintf(_t("<b>Click</b> on this option to change the %s of the block."), optionTooltipLabel),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: "click",
    };
}

<<<<<<< HEAD
function selectNested(trigger, optionName, alt_trigger = null, optionTooltipLabel = '', position = "top", allowPalette = false) {
    const noPalette = allowPalette ? '' : '.o_we_customize_panel:not(:has(.o_we_so_color_palette.o_we_widget_opened))';
    const option_block = `${noPalette} we-customizeblock-option[class='snippet-option-${optionName}']`;
    return {
        trigger: trigger,
        content: Markup(_.str.sprintf(_t("<b>Select</b> a %s."), optionTooltipLabel)),
=======
function selectNested(trigger, optionName, alt_trigger = null, optionTooltipLabel = '', position = "top") {
    const option_block = `we-customizeblock-option[class='snippet-option-${optionName}']`;
    return {
        trigger: trigger,
        content: _.str.sprintf(_t("<b>Select</b> a %s."), optionTooltipLabel),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        alt_trigger: alt_trigger == null ? undefined : `${option_block} ${alt_trigger}`,
        position: position,
        run: 'click',
        location: position === 'left' ? '#oe_snippets' : undefined,
    };
}

function changePaddingSize(direction) {
    let paddingDirection = "n";
    let position = "top";
    if (direction === "bottom") {
        paddingDirection = "s";
        position = "bottom";
    }
    return {
<<<<<<< HEAD
        trigger: `iframe .oe_overlay.ui-draggable.o_we_overlay_sticky.oe_active .o_handle.${paddingDirection}`,
        content: Markup(_.str.sprintf(_t("<b>Slide</b> this button to change the %s padding"), direction)),
=======
        trigger: `.oe_overlay.ui-draggable.o_we_overlay_sticky.oe_active .o_handle.${paddingDirection}`,
        content: _.str.sprintf(_t("<b>Slide</b> this button to change the %s padding"), direction),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        consumeEvent: 'mousedown',
        position: position,
    };
}

/**
 * Click on the top right edit button
 *
 * @deprecated use `clickOnEditAndWaitEditMode` instead to avoid race condition
 */
function clickOnEdit(position = "bottom") {
    return {
<<<<<<< HEAD
        trigger: ".o_menu_systray .o_edit_website_container a",
        content: Markup(_t("<b>Click Edit</b> to start designing your homepage.")),
        extra_trigger: "body:not(.editor_has_snippets)",
        position: position,
        timeout: 30000,
    };
}

/**
 * Simple click on an element in the page.
 * @param {*} elementName
 * @param {*} selector
 */
function clickOnElement(elementName, selector) {
    return {
        content: `Clicking on the ${elementName}`,
        trigger: selector,
        run: 'click'
=======
        trigger: "a[data-action=edit]",
        content: _t("<b>Click Edit</b> to start designing your homepage."),
        extra_trigger: ".homepage",
        position: position,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    };
}

/**
 * Click on the top right edit button and wait for the edit mode
 *
 * @param {string} position Where the purple arrow will show up
 */
function clickOnEditAndWaitEditMode(position = "bottom") {
    return [{
        content: _t("<b>Click Edit</b> to start designing your homepage."),
<<<<<<< HEAD
        trigger: ".o_menu_systray .o_edit_website_container a",
        position: position,
    }, {
        content: "Check that we are in edit mode",
        trigger: ".o_website_preview.editor_enable.editor_has_snippets",
=======
        trigger: "a[data-action=edit]",
        position: position,
    }, {
        content: "Check that we are in edit mode",
        trigger: '#oe_snippets.o_loaded',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        run: () => null, // it's a check
    }];
}

/**
 * Simple click on a snippet in the edition area
 * @param {*} snippet
 * @param {*} position
 */
function clickOnSnippet(snippet, position = "bottom") {
<<<<<<< HEAD
    const trigger = snippet.id ? `#wrapwrap .${snippet.id}` : snippet;
    return {
        trigger: `iframe ${trigger}`,
        extra_trigger: "body.editor_has_snippets",
        content: Markup(_t("<b>Click on a snippet</b> to access its options menu.")),
=======
    return {
        trigger: `#wrapwrap .${snippet.id}`,
        content: _t("<b>Click on a snippet</b> to access its options menu."),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: "click",
    };
}

function clickOnSave(position = "bottom") {
<<<<<<< HEAD
    return [{
        trigger: "div:not(.o_loading_dummy) > #oe_snippets button[data-action=\"save\"]:not([disabled])",
        // TODO this should not be needed but for now it better simulates what
        // an human does. By the time this was added, it's technically possible
        // to drag and drop a snippet then immediately click on save and have
        // some problem. Worst case probably is a traceback during the redirect
        // after save though so it's not that big of an issue. The problem will
        // of course be solved (or at least prevented in stable). More details
        // in related commit message.
        extra_trigger: "body:not(:has(.o_dialog)) #oe_snippets:not(:has(.o_we_already_dragging))",
        in_modal: false,
        content: Markup(_t("Good job! It's time to <b>Save</b> your work.")),
        position: position,
    }, {
        trigger: 'iframe body:not(.editor_enable)',
        noPrepend: true,
        auto: true, // Just making sure save is finished in automatic tests
        run: () => null,
    }];
=======
    return {
        trigger: "button[data-action=save]",
        in_modal: false,
        content: _t("Good job! It's time to <b>Save</b> your work."),
        position: position,
    };
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
}

/**
 * Click on a snippet's text to modify its content
 * @param {*} snippet
 * @param {*} element Target the element which should be rewrite
 * @param {*} position
 */
function clickOnText(snippet, element, position = "bottom") {
    return {
<<<<<<< HEAD
        trigger: snippet.id ? `iframe #wrapwrap .${snippet.id} ${element}` : snippet,
        extra_trigger: "iframe body.editor_enable",
        content: Markup(_t("<b>Click on a text</b> to start editing it.")),
        position: position,
        run: "text",
        consumeEvent: "click",
=======
        trigger: `#wrapwrap .${snippet.id} ${element}`,
        content: _t("<b>Click on a text</b> to start editing it."),
        position: position,
        run: "text",
        consumeEvent: "input",
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    };
}

/**
 * Drag a snippet from the Blocks area and drop it in the Edit area
 * @param {*} snippet contain the id and the name of the targeted snippet
 * @param {*} position Where the purple arrow will show up
 */
function dragNDrop(snippet, position = "bottom") {
    return {
        trigger: `#oe_snippets .oe_snippet[name="${snippet.name}"] .oe_snippet_thumbnail:not(.o_we_already_dragging)`,
<<<<<<< HEAD
        extra_trigger: ".o_website_preview.editor_enable.editor_has_snippets",
        content: Markup(_.str.sprintf(_t("Drag the <b>%s</b> building block and drop it at the bottom of the page."), snippet.name)),
        position: position,
        // Normally no main snippet can be dropped in the default footer but
        // targeting it allows to force "dropping at the end of the page".
        run: "drag_and_drop iframe #wrapwrap > footer",
=======
        extra_trigger: "body.editor_enable.editor_has_snippets",
        moveTrigger: '.oe_drop_zone',
        content: _.str.sprintf(_t("Drag the <b>%s</b> building block and drop it at the bottom of the page."), snippet.name),
        position: position,
        // Normally no main snippet can be dropped in the default footer but
        // targeting it allows to force "dropping at the end of the page".
        run: "drag_and_drop #wrapwrap > footer",
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    };
}

function goBackToBlocks(position = "bottom") {
    return {
        trigger: '.o_we_add_snippet_btn',
        content: _t("Click here to go back to block tab."),
        position: position,
        run: "click",
    };
}

<<<<<<< HEAD
function goToTheme(position = "bottom") {
    return {
        trigger: '.o_we_customize_theme_btn',
        extra_trigger: '#oe_snippets.o_loaded',
        content: _t("Go to the Theme tab"),
=======
function goToOptions(position = "bottom") {
    return {
        trigger: '.o_we_customize_theme_btn',
        content: _t("Go to the Options tab"),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: "click",
    };
}

function selectHeader(position = "bottom") {
    return {
<<<<<<< HEAD
        trigger: `iframe header#top`,
        content: Markup(_t(`<b>Click</b> on this header to configure it.`)),
=======
        trigger: `header#top`,
        content: _t(`<b>Click</b> on this header to configure it.`),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        position: position,
        run: "click",
    };
}

function selectSnippetColumn(snippet, index = 0, position = "bottom") {
     return {
<<<<<<< HEAD
        trigger: `iframe #wrapwrap .${snippet.id} .row div[class*="col-lg-"]:eq(${index})`,
        content: Markup(_t("<b>Click</b> on this column to access its options.")),
=======
        trigger: `#wrapwrap .${snippet.id} .row div[class*="col-lg-"]:eq(${index})`,
        content: _t("<b>Click</b> on this column to access its options."),
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
         position: position,
        run: "click",
     };
}

function prepend_trigger(steps, prepend_text='') {
    for (const step of steps) {
        if (!step.noPrepend && prepend_text) {
            step.trigger = prepend_text + step.trigger;
        }
    }
    return steps;
}

<<<<<<< HEAD
function getClientActionUrl(path, edition) {
    let url = `/web#action=website.website_preview`;
    if (path) {
        url += `&path=${encodeURIComponent(path)}`;
    }
    if (edition) {
        url += '&enable_editor=1';
    }
    return url;
}

function clickOnExtraMenuItem(stepOptions, backend = false) {
    return Object.assign({}, {
        content: "Click on the extra menu dropdown toggle if it is there",
        trigger: `${backend ? "iframe" : ""} #top_menu`,
        run: function () {
            const extraMenuButton = this.$anchor[0].querySelector('.o_extra_menu_items a.nav-link');
            if (extraMenuButton) {
                extraMenuButton.click();
            }
        },
    }, stepOptions);
}

/**
 * Registers a tour that will go in the website client action.
 *
 * @param {string} name The tour's name
 * @param {object} options The tour options
 * @param {string} options.url The page to edit
 * @param {boolean} [options.edition] If the tour starts in edit mode
 * @param {object[]} steps The steps of the tour
 */
function registerWebsitePreviewTour(name, options, steps) {
    const tourSteps = [...steps];
    const url = getClientActionUrl(options.url, !!options.edition);

    // Note: for both non edit mode and edit mode, we set a high timeout for the
    // first step. Indeed loading both the backend and the frontend (in the
    // iframe) and potentially starting the edit mode can take a long time in
    // automatic tests. We'll try and decrease the need for this high timeout
    // of course.
    if (options.edition) {
        tourSteps.unshift({
            content: "Wait for the edit mode to be started",
            trigger: '.o_website_preview.editor_enable.editor_has_snippets',
            timeout: 30000,
            auto: true,
            run: () => {}, // It's a check
        });
    } else {
        tourSteps[0].timeout = 20000;
    }

    return tour.register(name, Object.assign({}, options, { url }), tourSteps);
}

function registerThemeHomepageTour(name, steps) {
    return registerWebsitePreviewTour(name, {
        url: '/',
        edition: true,
        sequence: 1010,
        saveAs: "homepage",
    }, prepend_trigger(
        steps.concat(clickOnSave()),
        ".o_website_preview[data-view-xmlid='website.homepage'] "
    ));
}

function registerBackendAndFrontendTour(name, options, steps) {
    if (window.location.pathname === '/web') {
        const newSteps = [];
        for (const step of steps) {
            const newStep = Object.assign({}, step);
            newStep.trigger = `iframe ${step.trigger}`;
            if (step.extra_trigger) {
                newStep.extra_trigger = `iframe ${step.extra_trigger}`;
            }
            newSteps.push(newStep);
        }
        return registerWebsitePreviewTour(name, options, newSteps);
    }

    return tour.register(name, {
        url: options.url,
    }, steps);
}

/**
 * Selects an element inside a we-select, if the we-select is from a m2o widget, searches for it.
 *
 * @param widgetName {string} The widget's data-name
 * @param elementName {string} the element to search
 * @param searchNeeded {Boolean} if the widget is a m2o widget and a search is needed
 */
function selectElementInWeSelectWidget(widgetName, elementName, searchNeeded = false) {
    const steps = [clickOnElement(`${widgetName} toggler`, `we-select[data-name=${widgetName}] we-toggler`)];

    if (searchNeeded) {
        steps.push({
            content: `Inputing ${elementName} in m2o widget search`,
            trigger: `we-select[data-name=${widgetName}] div.o_we_m2o_search input`,
            run: `text ${elementName}`
        });
    }
    steps.push(clickOnElement(`${elementName} in the ${widgetName} widget`,
        `we-select[data-name=${widgetName}] we-button:contains(${elementName})`));
    return steps;
}

return {
    addMedia,
    assertCssVariable,
    assertPathName,
=======
function registerThemeHomepageTour(name, steps) {
    tour.register(name, {
        url: "/?enable_editor=1",
        sequence: 1010,
        saveAs: "homepage",
    }, prepend_trigger(
        steps,
        "html[data-view-xmlid='website.homepage'] "
    ));
}


return {
    addMedia,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    changeBackground,
    changeBackgroundColor,
    changeColumnSize,
    changeIcon,
    changeImage,
    changeOption,
    changePaddingSize,
    clickOnEdit,
<<<<<<< HEAD
    clickOnElement,
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    clickOnEditAndWaitEditMode,
    clickOnSave,
    clickOnSnippet,
    clickOnText,
    dragNDrop,
    goBackToBlocks,
<<<<<<< HEAD
    goToTheme,
=======
    goToOptions,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    selectColorPalette,
    selectHeader,
    selectNested,
    selectSnippetColumn,
<<<<<<< HEAD
    getClientActionUrl,
    registerThemeHomepageTour,
    clickOnExtraMenuItem,
    registerWebsitePreviewTour,
    registerBackendAndFrontendTour,
    selectElementInWeSelectWidget,
=======

    registerThemeHomepageTour,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
};
});
