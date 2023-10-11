# -*- coding: utf-8 -*-
from odoo import fields, models

class AccountAsset(models.Model):
    _inherit = "account.asset"

    tipo_de_activo = fields.Selection([
        ('tangible', 'Tangible'), 
        ('intangible', 'Intangible'),
        ], string='Tipo de Activo')