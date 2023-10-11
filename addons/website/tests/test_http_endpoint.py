# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
<<<<<<< HEAD
from odoo.tests import HttpCase

import werkzeug
=======
from unittest.mock import sentinel

from odoo.http import EndPoint
from odoo.tests import HttpCase
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe


class TestHttpEndPoint(HttpCase):

<<<<<<< HEAD
=======
    def test_http_endpoint_equality(self):
        sentinel.method.original_func = sentinel.method_original_func
        args = (sentinel.method, {'routing_arg': sentinel.routing_arg})
        endpoint1 = EndPoint(*args)
        endpoint2 = EndPoint(*args)

        self.assertEqual(endpoint1, endpoint2)

        testdict = {}
        testdict[endpoint1] = 42
        self.assertEqual(testdict[endpoint2], 42)
        self.assertTrue(endpoint2 in testdict)

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    def test_can_clear_routing_map_during_render(self):
        """
        The routing map might be cleared while rendering a qweb view.
        For example, if an asset bundle is regenerated the old one is unlinked,
        which causes a cache clearing.
        This test ensures that the rendering still works, even in this case.
        """
<<<<<<< HEAD
        homepage_view = self.env['ir.ui.view'].search([
=======
        homepage_id = self.env['ir.ui.view'].search([
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            ('website_id', '=', self.env.ref('website.default_website').id),
            ('key', '=', 'website.homepage'),
        ])
        self.env['ir.ui.view'].create({
            'name': 'Add cache clear to Home',
            'type': 'qweb',
            'mode': 'extension',
<<<<<<< HEAD
            'inherit_id': homepage_view.id,
=======
            'inherit_id': homepage_id.id,
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            'arch_db': """
                <t t-call="website.layout" position="before">
                    <t t-esc="website.env['ir.http']._clear_routing_map()"/>
                </t>
            """,
        })

        r = self.url_open('/')
        r.raise_for_status()
<<<<<<< HEAD

    def test_redirect_double_slash(self):
        res = self.url_open('/test_http//greeting', allow_redirects=False)
        self.assertIn(res.status_code, (301, 308))
        self.assertEqual(werkzeug.urls.url_parse(res.headers.get('Location', '')).path, '/test_http/greeting')
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
