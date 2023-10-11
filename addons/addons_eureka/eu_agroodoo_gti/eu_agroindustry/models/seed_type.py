# -*- coding: utf-8 -*-

from odoo import models, fields

class SeedType(models.Model):
    _name = 'seed.type'
    _description = "Tipo de semilla"

    name = fields.Char("Nombre")