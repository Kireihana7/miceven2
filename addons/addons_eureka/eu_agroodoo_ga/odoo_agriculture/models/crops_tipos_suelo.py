# -*- coding: utf-8 -*-
from odoo import api, fields, models  

class CropsTiposSuelo(models.Model):
    _name = 'crops.tipos.suelo'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(
        string='Name',
        required=True,
        tracking=True
    )

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The soil type entered already exists'),
    ]    