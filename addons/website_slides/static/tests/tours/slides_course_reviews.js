<<<<<<< HEAD:addons/website_slides/static/tests/tours/slides_course_reviews.js
/** @odoo-module **/

import tour from 'web_tour.tour';
=======
odoo.define('website_slides.tour.slide.course.reviews', function (require) {
'use strict';

const tour = require('web_tour.tour');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/website_slides/static/src/tests/tours/slides_course_reviews.js

/**
 * This tour test that a log note isn't considered
 * as a course review. And also that a member can
 * add only one review.
 */
tour.register('course_reviews', {
    url: '/slides',
    test: true
}, [
{
    trigger: 'a:contains("Basics of Gardening - Test")',
}, {
    trigger: 'a[id="review-tab"]',
}, {
    trigger: '.o_portal_chatter_message:contains("Log note")',
    run: function() {},
}, {
<<<<<<< HEAD:addons/website_slides/static/tests/tours/slides_course_reviews.js
    trigger: 'span:contains("Add Review")',
    // If it fails here, it means the log note is considered as a review
}, {
    trigger: 'div.o_portal_chatter_composer_body textarea',
    extra_trigger: 'div.modal_shown',
=======
    trigger: 'button:contains("Add a review")',
    // If it fails here, it means the log note is considered as a review
}, {
    trigger: 'form.o_portal_chatter_composer_form textarea',
    extra_trigger: 'div#ratingpopupcomposer.modal_shown',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/website_slides/static/src/tests/tours/slides_course_reviews.js
    run: 'text Great course!',
    in_modal: false,
}, {
    trigger: 'button.o_portal_chatter_composer_btn',
    in_modal: false,
}, {
    trigger: 'a[id="review-tab"]',
}, {
    trigger: 'button:contains("Visible")',
}, {
<<<<<<< HEAD:addons/website_slides/static/tests/tours/slides_course_reviews.js
    trigger: 'span:contains("Edit Review")',
    // If it fails here, it means the system is allowing you to add another review.
}, {
    trigger: 'div.o_portal_chatter_composer_body textarea:contains("Great course!")',
    run: function() {},
}
]);
=======
    trigger: 'button:contains("Modify your review")',
    // If it fails here, it means the system is allowing you to add another review.
}, {
    trigger: 'form.o_portal_chatter_composer_form textarea:contains("Great course!")',
    run: function() {},
}
]);

});
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/website_slides/static/src/tests/tours/slides_course_reviews.js
