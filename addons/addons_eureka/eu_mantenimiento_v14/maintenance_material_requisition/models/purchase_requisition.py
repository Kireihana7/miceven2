# -*- coding: utf-8 -*-

from odoo import models, fields

class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'
    
    custom_maintenance_id = fields.Many2one(
        'maintenance.request',
        string='Mantenimiento',
        copy=False,
    )
