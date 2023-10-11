# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from . import models
<<<<<<< HEAD:addons/privacy_lookup/__init__.py
from . import wizard
=======
from odoo import api, SUPERUSER_ID

def l10n_eu_service_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.company']._map_all_eu_companies_taxes()

def l10n_eu_service_uninstall(cr, registry):
    cr.execute("DELETE FROM ir_model_data WHERE module = 'l10n_eu_service' and model in ('account.tax.group', 'account.account');")
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe:addons/l10n_eu_service/__init__.py
