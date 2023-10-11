# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from werkzeug.exceptions import BadRequest
<<<<<<< HEAD
=======
from werkzeug.utils import redirect
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

from odoo import http
from odoo.http import request


class GoogleAuth(http.Controller):

    @http.route('/google_account/authentication', type='http', auth="public")
    def oauth2callback(self, **kw):
        """ This route/function is called by Google when user Accept/Refuse the consent of Google """
        state = json.loads(kw.get('state', '{}'))
<<<<<<< HEAD
        service = state.get('s')
        url_return = state.get('f')
        if (not service or (kw.get('code') and not url_return)):
            raise BadRequest()

        if kw.get('code'):
            base_url = request.httprequest.url_root.strip('/') or request.env.user.get_base_url()
            access_token, refresh_token, ttl = request.env['google.service']._get_google_tokens(
                kw['code'],
                service,
                redirect_uri=f'{base_url}/google_account/authentication'
            )
            service_field = f'google_{service}_account_id'
            if service_field in request.env.user:
                getattr(request.env.user, service_field)._set_auth_tokens(access_token, refresh_token, ttl)
=======
        dbname = state.get('d')
        service = state.get('s')
        url_return = state.get('f')
        base_url = request.httprequest.url_root.strip('/')
        if (not dbname or not service or (kw.get('code') and not url_return)):
            raise BadRequest()

        with registry(dbname).cursor() as cr:
            if kw.get('code'):
                access_token, refresh_token, ttl = request.env['google.service'].with_context(base_url=base_url)._get_google_tokens(kw['code'], service)
                # LUL TODO only defined in google_calendar
                request.env.user._set_auth_tokens(access_token, refresh_token, ttl)
                return redirect(url_return)
            elif kw.get('error'):
                return redirect("%s%s%s" % (url_return, "?error=", kw['error']))
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            else:
                raise Warning('No callback field for service <%s>' % service)
            return request.redirect(url_return)
        elif kw.get('error'):
            return request.redirect("%s%s%s" % (url_return, "?error=", kw['error']))
        else:
            return request.redirect("%s%s" % (url_return, "?error=Unknown_error"))
