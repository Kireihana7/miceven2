# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import hashlib
import json
from odoo.exceptions import UserError
from odoo import api, models
from odoo.http import request
from odoo.tools import ustr
from odoo.addons.web.controllers.main import module_boot, HomeStaticTemplateHelpers
import odoo

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        version_info = odoo.service.common.exp_version()

        user_context = request.session.get_context() if request.session.uid else {}

        session_info = {
            "uid": request.session.uid,
            "is_system": user._is_system() if request.session.uid else False,
            "is_admin": user._is_admin() if request.session.uid else False,
            "user_context": request.session.get_context() if request.session.uid else {},
            "db": request.session.db,
            "server_version": version_info.get('server_version'),
            "server_version_info": version_info.get('server_version_info'),
            "name": user.name,
            "username": user.login,
            "partner_display_name": user.partner_id.display_name,
            "company_id": user.company_id.id if request.session.uid else None,  # YTI TODO: Remove this from the user context
            "branch_id": user.branch_id.id if request.session.uid else None,
            "partner_id": user.partner_id.id if request.session.uid and user.partner_id else None,
            "web.base.url": self.env['ir.config_parameter'].sudo().get_param('web.base.url', default=''),
        }
        if self.env.user.has_group('base.group_user'):
            # the following is only useful in the context of a webclient bootstrapping
            # but is still included in some other calls (e.g. '/web/session/authenticate')
            # to avoid access errors and unnecessary information, it is only included for users
            # with access to the backend ('internal'-type users)
            mods = module_boot()
            qweb_checksum = HomeStaticTemplateHelpers.get_qweb_templates_checksum(addons=mods, debug=request.session.debug)
            lang = user_context.get("lang")
            translation_hash = request.env['ir.translation'].get_web_translations_hash(mods, lang)
            menu_json_utf8 = json.dumps(request.env['ir.ui.menu'].load_menus(request.session.debug), default=ustr, sort_keys=True).encode()
            cache_hashes = {
                "load_menus": hashlib.sha1(menu_json_utf8).hexdigest(),
                "qweb": qweb_checksum,
                "translations": translation_hash,
            }
            session_info.update({
                # current_company should be default_company
                "user_companies": {'current_company': (user.company_id.id, user.company_id.name), 'allowed_companies': [(comp.id, comp.name) for comp in user.company_ids]},
                "user_branches": {'current_branch': (user.branch_id.id, user.branch_id.name,user.branch_id.company_id.id), 'allowed_branch': [(comp.id, comp.name,comp.company_id.id) for comp in user.branch_ids]},
                "currencies": self.get_currencies(),
                "show_effect": True,
                "display_switch_company_menu": user.has_group('base.group_multi_company') and len(user.company_ids) > 1,
                "display_switch_branch_menu": user.has_group('branch.group_multi_branch') and len(user.branch_ids) > 1,
                "cache_hashes": cache_hashes,
                "allowed_branch_ids" : [ (p.id,p.company_id.id) for p in user.branch_ids]
            })

        return session_info
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: