odoo.define("website_mass_mailing.tour.newsletter_popup_edition", function (require) {
"use strict";

<<<<<<< HEAD
const wTourUtils = require('website.tour_utils');
const newsletterPopupUseTour = require('website_mass_mailing.tour.newsletter_popup_use');

wTourUtils.registerWebsitePreviewTour("newsletter_popup_edition", {
    test: true,
    url: "/",
    edition: true,
=======
const tour = require('web_tour.tour');
const wTourUtils = require('website.tour_utils');

tour.register('newsletter_popup_edition', {
    test: true,
    url: '/?enable_editor=1',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
}, [
    wTourUtils.dragNDrop({
        id: 's_newsletter_subscribe_popup',
        name: 'Newsletter Popup',
    }),
    {
<<<<<<< HEAD
        content: "Check the modal is opened for edition",
        trigger: 'iframe .o_newsletter_popup .modal:visible',
        in_modal: false,
        run: () => null,
    },
    ...wTourUtils.clickOnSave(),
    {
        content: "Check the modal has been saved, closed",
        trigger: 'iframe body:has(.o_newsletter_popup)',
        extra_trigger: 'iframe body:not(.editor_enable)',
        run: newsletterPopupUseTour.ensurePopupNotVisible,
    }
=======
        content: "Confirm newsletter choice",
        trigger: '.modal-footer .btn-primary',
    },
    {
        content: "Check the modal is opened for edition",
        trigger: '.o_newsletter_popup .modal:visible',
        in_modal: false,
        run: () => null,
    },
    wTourUtils.clickOnSave(),
    {
        content: "Check the modal has been saved, closed",
        trigger: '.o_newsletter_popup',
        extra_trigger: 'body:not(.editor_enable)',
        run: function (actions) {
            const $modal = this.$anchor.find('.modal');
            if ($modal.is(':visible')) {
                console.error('Modal is still opened...');
            }
        },
    },
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
]);
});

odoo.define("website_mass_mailing.tour.newsletter_popup_use", function (require) {
"use strict";

const tour = require('web_tour.tour');

<<<<<<< HEAD
function ensurePopupNotVisible() {
    const $modal = this.$anchor.find('.o_newsletter_popup .modal');
    if ($modal.length !== 1) {
        // Avoid the tour to succeed if the modal can't be found while
        // it should. Indeed, if the selector ever becomes wrong and the
        // expected element is actually not found anymore, the test
        // won't be testing anything anymore as the visible check will
        // always be truthy on empty jQuery element.
        console.error("Modal couldn't be found in the DOM. The tour is not working as expected.");
    }
    if ($modal.is(':visible')) {
        console.error('Modal should not be opened.');
    }
}

=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
tour.register('newsletter_popup_use', {
    test: true,
    url: '/',
}, [
    {
        content: "Check the modal is not yet opened and force it opened",
<<<<<<< HEAD
        trigger: 'body:has(.o_newsletter_popup)',
        run: ensurePopupNotVisible,
=======
        trigger: '.o_newsletter_popup',
        run: function (actions) {
            const $modal = this.$anchor.find('.modal');
            if ($modal.is(':visible')) {
                console.error('Modal is already opened...');
            }
            $(document).trigger('mouseleave');
        },
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
    {
        content: "Check the modal is now opened and enter text in the subscribe input",
        trigger: '.o_newsletter_popup .modal input',
        in_modal: false,
        run: 'text hello@world.com',
    },
    {
        content: "Subscribe",
        trigger: '.modal-dialog .btn-primary',
    },
    {
        content: "Check the modal is now closed",
<<<<<<< HEAD
        trigger: 'body:has(.o_newsletter_popup)',
        run: ensurePopupNotVisible,
    }
]);

return {
    ensurePopupNotVisible: ensurePopupNotVisible,
};
=======
        trigger: '.o_newsletter_popup',
        run: function (actions) {
            const $modal = this.$anchor.find('.modal');
            if ($modal.is(':visible')) {
                console.error('Modal is still opened...');
            }
        },
    }
]);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
});
