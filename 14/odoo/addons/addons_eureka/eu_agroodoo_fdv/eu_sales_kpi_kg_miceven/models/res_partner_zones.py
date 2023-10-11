# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartnerZones(models.Model):
    _inherit = "res.partner.zones"

    manager_id = fields.Many2one("hr.employee", "Mánager", tracking=True)
    crm_team_ids = fields.One2many("crm.team", "zone_id", "Equipos de venta", tracking=True)