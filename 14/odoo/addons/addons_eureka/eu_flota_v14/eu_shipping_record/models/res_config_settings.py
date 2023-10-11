# -*- coding: utf-8 -*-

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    can_invoice_trip = fields.Boolean(
        "Puede facturar viajes", 
        config_parameter="eu_shipping_record.can_invoice_trip"
    )