# -*- coding: utf-8 -*-

from odoo import models, fields

class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'
    
    custom_fleet_id = fields.Many2one(
        'fleet.vehicle',
        string='Flota / Vehículo',
        copy=False,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
