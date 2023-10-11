# -*- coding: utf-8 -*-

from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    crm_team_ids = fields.One2many("crm.team", "user_id", "Equipos de venta", tracking=True)