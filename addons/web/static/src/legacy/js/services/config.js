odoo.define('web.config', function (require) {
"use strict";

const Bus = require('web.Bus');
const { hasTouch, isAndroid, isIOS, isMobileOS } = require('@web/core/browser/feature_detection');
const { getMediaQueryLists } = require('@web/core/ui/ui_service');

const bus = new Bus();

/**
 * This module contains all the (mostly) static 'environmental' information.
 * This is often necessary to allow the rest of the web client to properly
 * render itself.
 *
 * Note that many information currently stored in session should be moved to
 * this file someday.
 */

const maxTouchPoints = navigator.maxTouchPoints || 1;
const isAndroid = /Android/i.test(navigator.userAgent);
const isIOS = /(iPad|iPhone|iPod)/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && maxTouchPoints > 1);
const isOtherMobileDevice = /(webOS|BlackBerry|Windows Phone)/i.test(navigator.userAgent);

var config = {
    device: {
        /**
        * bus to use in order to be able to handle device config related events
        *   - 'size_changed' : triggered when window size is
        *     corresponding to a new bootstrap breakpoint. The new size_class
         *    is provided.
        */
        bus: bus,
        /**
         * touch is a boolean, true if the device supports touch interaction
         *
         * @type Boolean
         */
        touch: hasTouch(),
        /**
         * size_class is an integer: 0, 1, 2, 3 or 4, depending on the (current)
         * size of the device.  This is a dynamic property, updated whenever the
         * browser is resized
         *
         * @type Number
         */
        size_class: null,
        /**
         * Mobile OS (Android) device detection using userAgent.
         * This flag doesn't depend on the size/resolution of the screen.
         *
         * @return Boolean
         */
<<<<<<< HEAD:addons/web/static/src/legacy/js/services/config.js
        isAndroid: isAndroid(),
=======
        isAndroid: isAndroid,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/web/static/src/js/services/config.js
        /**
         * Mobile OS (iOS) device detection using userAgent.
         * This flag doesn't depend on the size/resolution of the screen.
         *
         * @return Boolean
         */
<<<<<<< HEAD:addons/web/static/src/legacy/js/services/config.js
        isIOS: isIOS(),
=======
        isIOS: isIOS,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/web/static/src/js/services/config.js
        /**
         * A frequent use case is to have a different render in 'mobile' mode,
         * meaning when the screen is small.  This flag (boolean) is true when
         * the size is XS/VSM/SM. It is also updated dynamically.
         *
         * @type Boolean
         */
        isMobile: null,
        /**
         * Mobile device detection using userAgent.
         * This flag doesn't depend on the size/resolution of the screen.
         * It targets mobile devices which suggests that there is a virtual keyboard.
         *
         * @return {boolean}
         */
<<<<<<< HEAD:addons/web/static/src/legacy/js/services/config.js
        isMobileDevice: isMobileOS(),
=======
        isMobileDevice: isAndroid || isIOS || isOtherMobileDevice,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/web/static/src/js/services/config.js
        /**
         * Mapping between the numbers 0,1,2,3,4,5,6 and some descriptions
         */
        SIZES: { XS: 0, VSM: 1, SM: 2, MD: 3, LG: 4, XL: 5, XXL: 6 },
    },
    /**
     * States whether the current environment is in debug or not.
     *
     * @param debugMode the debug mode to check, empty for simple debug mode
     * @returns {boolean}
     */
    isDebug: function (debugMode) {
        if (debugMode) {
            return odoo.debug && odoo.debug.indexOf(debugMode) !== -1;
        }
        return odoo.debug;
    },
};

const medias = getMediaQueryLists();

/**
 * Return the current size class
 *
 * @returns {integer} a number between 0 and 5, included
 */
function _getSizeClass() {
    for (var i = 0 ; i < medias.length ; i++) {
        if (medias[i].matches) {
            return i;
        }
    }
}
/**
 * Update the size dependant properties in the config object.  This method
 * should be called every time the size class changes.
 */
function _updateSizeProps() {
    var sc = _getSizeClass();
    if (sc !== config.device.size_class) {
        config.device.size_class = sc;
        config.device.isMobile = config.device.size_class <= config.device.SIZES.SM;
        config.device.bus.trigger('size_changed', config.device.size_class);
    }
}

_.invoke(medias, 'addListener', _updateSizeProps);
_updateSizeProps();

return config;

});
