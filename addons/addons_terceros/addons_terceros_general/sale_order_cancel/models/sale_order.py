#coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class sale_order(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(selection_add=[('anular', 'Anulada')])
        
    def button_cancel_order(self):
        for rec in self:
            for lines in rec.order_line:
                if lines.qty_delivered!=0:
                    raise UserError(_('No puedes eliminar un Pedido de Venta que tenga cantidad entregada.'))
                if lines.qty_invoiced!=0:
                    raise UserError(_('No puedes eliminar un Pedido de Venta que tenga cantidad facturadas.'))    
                rec.state = 'anular'


    def action_cancel(self):
        for rec in self:
            for lines in rec.order_line:
                if lines.qty_delivered!=0:
                    raise UserError(_('No puedes eliminar un Pedido de Venta que tenga cantidad entregada.'))
                if lines.qty_invoiced!=0:
                    raise UserError(_('No puedes eliminar un Pedido de Venta que tenga cantidad facturadas.'))    
        return super(sale_order, self).action_cancel()