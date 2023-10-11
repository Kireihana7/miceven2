# -*- coding: utf-8 -*-

from odoo import models, fields

class RequisitionOnBottom(models.Model):
    _inherit = "purchase.requisition"
    
    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisiciones',
        copy=False
    )
class RequisitionOrderLine(models.Model):
    _inherit = 'purchase.requisition.line'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Línea de Requisiciones',
        copy=False
    )

