# -*- coding: utf-8 -*-

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    api_eos_key = fields.Char(
        "API EOS", 
        config_parameter='eu_eos_integration.api_eos_key',
    )