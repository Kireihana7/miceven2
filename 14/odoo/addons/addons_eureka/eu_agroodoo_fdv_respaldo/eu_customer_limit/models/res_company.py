# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    maximo_deuda_permitida = fields.Float(string="Máximo de Deuda Permitida")