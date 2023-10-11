#coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    """
    Re-write to add check lists as a part of work flow
    """
    _inherit = "purchase.order"

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('anular', 'Anulada'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    def button_cancel_order(self):
        for rec in self:
            for lines in rec.order_line:
                if lines.qty_received!=0:
                    raise UserError(_('No puedes eliminar un Pedido de Compra que tenga cantidad entregada.'))
                if lines.qty_invoiced!=0:
                    raise UserError(_('No puedes eliminar un Pedido de Compra que tenga cantidad facturadas.'))    
                rec.state = 'anular'