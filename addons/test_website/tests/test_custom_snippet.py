# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo.tests
from odoo.tools import mute_logger


@odoo.tests.common.tagged('post_install', '-at_install')
class TestCustomSnippet(odoo.tests.HttpCase):

    @mute_logger('odoo.addons.http_routing.models.ir_http', 'odoo.http')
    def test_01_run_tour(self):
<<<<<<< HEAD
        self.start_tour(self.env['website'].get_client_action_url('/'), 'test_custom_snippet', login="admin")
=======
        self.start_tour("/", 'test_custom_snippet', login="admin")
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
