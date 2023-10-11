# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

<<<<<<< HEAD
<<<<<<<< HEAD:addons/hw_drivers/http.py
import odoo


def db_list(force=False, host=None):
    return []

odoo.http.db_list = db_list
========
# Copyright (c) 2011 Noviat nv/sa (www.noviat.be). All rights reserved.
>>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/l10n_be_invoice_bba/__init__.py
=======
from odoo import http


class IoTBoxHttpRequest(http.HttpRequest):
    def dispatch(self):
        if self._is_cors_preflight(http.request.endpoint):
            # Using the PoS in debug mode in v12, the call to '/hw_proxy/handshake' contains the
            # 'X-Debug-Mode' header, which was removed from 'Access-Control-Allow-Headers' in v13.
            # When the code of http.py is not checked out to v12 (i.e. in Community), the connection
            # fails as the header is rejected and none of the devices can be used.
            headers = {
                'Access-Control-Max-Age': 60 * 60 * 24,
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization, X-Debug-Mode'
            }
            return http.Response(status=200, headers=headers)
        return super(IoTBoxHttpRequest, self).dispatch()


class IoTBoxRoot(http.Root):
    def setup_db(self, httprequest):
        # No database on the IoT Box
        pass

    def get_request(self, httprequest):
        # Override HttpRequestwith IoTBoxHttpRequest
        if httprequest.mimetype not in ("application/json", "application/json-rpc"):
            return IoTBoxHttpRequest(httprequest)
        return super(IoTBoxRoot, self).get_request(httprequest)

http.Root = IoTBoxRoot
http.root = IoTBoxRoot()
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
