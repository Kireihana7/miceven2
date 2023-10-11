# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    terceros_autorizados = fields.One2many('res.partner.autorizados','partner_id',string="Autorizados")
