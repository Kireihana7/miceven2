# -*- coding: utf-8 -*-
from odoo import _, api, fields, models  # noqa

class PartnerZone(models.Model):
    _name = "partner.zone"
    _description = "Division of contacts by geographical commercial area"

    name = fields.Char(string="Zone", required=True)
    city = fields.Char(string="City", required=True)
    state_id = fields.Many2one(
        "res.country.state",
        required=True,
        string="State",
        ondelete="restrict",
        domain="[('country_id', '=?', country_id)]",
    )
    country_id = fields.Many2one(
        "res.country", required=True, string="Country", ondelete="restrict"
    )
