# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class PurchaseSourceWarehouse(models.Model):
    _name = "purchase.source.warehouse"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre", tracking=True) 