odoo.define('website.s_showcase_options', function (require) {
'use strict';

const options = require('web_editor.snippets.options');

options.registry.Showcase = options.Class.extend({
    /**
     * @override
     */
    onMove: function () {
        const $showcaseCol = this.$target.parent().closest('.row > div');
        const isLeftCol = $showcaseCol.index() <= 0;
        const $title = this.$target.children('.s_showcase_title');
        $title.toggleClass('flex-lg-row-reverse', isLeftCol);
<<<<<<< HEAD
        $showcaseCol.find('.s_showcase_icon.ms-3').removeClass('ms-3').addClass('ms-lg-3'); // For compatibility with old version
        $title.find('.s_showcase_icon').toggleClass('me-lg-0 ms-lg-3', isLeftCol);
=======
        $showcaseCol.find('.s_showcase_icon.ml-3').removeClass('ml-3').addClass('ml-lg-3'); // For compatibility with old version
        $title.find('.s_showcase_icon').toggleClass('mr-lg-0 ml-lg-3', isLeftCol);
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    },
});
});
