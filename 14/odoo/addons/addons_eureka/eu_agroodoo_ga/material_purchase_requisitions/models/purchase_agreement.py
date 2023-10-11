# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.agreement'
    
    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisiciones',
        copy=False
    )
    
    def action_confirm(self):
        for rec in self:
            if rec.custom_requisition_id.state == '7':
                raise UserError('No puedes confirmar una Licitación con la requisición Rechazada')
        return super(PurchaseOrder, self).action_confirm()

    def action_confirm_auto(self):
        for rec in self:
            if rec.custom_requisition_id.state == '7':
                raise UserError('No puedes confirmar una Licitación con la requisición Rechazada')
        return super(PurchaseOrder, self).action_confirm_auto()
    def action_cancel(self):
        for rec in self:
            if rec.custom_requisition_id and not rec.sh_purchase_agreement_line_ids:
                rec.custom_requisition_id.action_cancel()
        return super().action_cancel()
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.agreement.line'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Línea de Requisiciones',
        copy=False
    )

