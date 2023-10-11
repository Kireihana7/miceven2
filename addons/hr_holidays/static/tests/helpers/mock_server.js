<<<<<<< HEAD
/** @odoo-module **/

import '@mail/../tests/helpers/mock_server'; // ensure mail overrides are applied first

import { patch } from "@web/core/utils/patch";
import { MockServer } from "@web/../tests/helpers/mock_server";

patch(MockServer.prototype, 'hr_holidays', {
    /**
     * Overrides to add out of office to employees.
     *
     * @override
     */
    _mockResPartnerMailPartnerFormat(ids) {
        const partnerFormats = this._super(...arguments);
        const partners = this.getRecords(
=======
odoo.define('hr_holidays/static/tests/helpers/mock_server.js', function (require) {
'use strict';

require('mail.MockServer'); // ensure mail overrides are applied first

const MockServer = require('web.MockServer');

MockServer.include({
    /**
     * Overrides to add visitor information to livechat channels.
     *
     * @override
     */
    _mockMailChannelPartnerInfo(ids, extra_info) {
        const partnerInfos = this._super(...arguments);
        const partners = this._getRecords(
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            'res.partner',
            [['id', 'in', ids]],
            { active_test: false },
        );
        for (const partner of partners) {
            // Not a real field but ease the testing
<<<<<<< HEAD
            partnerFormats.get(partner.id).out_of_office_date_end = partner.out_of_office_date_end;
        }
        return partnerFormats;
    },
});
=======
            partnerInfos[partner.id].out_of_office_date_end = partner.out_of_office_date_end;
        }
        return partnerInfos;
    },
});

});
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
