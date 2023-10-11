# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

<<<<<<< HEAD
from odoo import fields, models, api
=======
from odoo import api, fields, models
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

<<<<<<< HEAD
    # pos.config fields
    pos_adyen_ask_customer_for_tip = fields.Boolean(compute='_compute_pos_adyen_ask_customer_for_tip', store=True, readonly=False)

    @api.depends('pos_iface_tipproduct', 'pos_config_id')
    def _compute_pos_adyen_ask_customer_for_tip(self):
        for res_config in self:
            if res_config.pos_iface_tipproduct:
                res_config.pos_adyen_ask_customer_for_tip = res_config.pos_config_id.adyen_ask_customer_for_tip
            else:
                res_config.pos_adyen_ask_customer_for_tip = False
=======
    adyen_account_id = fields.Many2one(string='Adyen Account', related='company_id.adyen_account_id')

    def create_adyen_account(self):
        return self.env['adyen.account'].action_create_redirect()
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
