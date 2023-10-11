# -*- coding: utf-8 -*-

from odoo import models, fields,api
from odoo.exceptions import UserError
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisiciones',
        copy=False
    )
    @api.model
    def create(self,vals):
        res=super().create(vals)
        for rec in res:
            if rec.agreement_id and rec.agreement_id.custom_requisition_id:
                rec.picking_type_id= rec.agreement_id.custom_requisition_id.custom_picking_type_id
        return res
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Línea de Requisiciones',
        copy=False
    )
    

