# -*- coding: utf-8 -*-
from odoo import models,fields

class PurchaseOrder(models.Model):
    _inherit="purchase.order"
        
    zona_productor=fields.Char(string="Zona")