#coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import UserError




class sale_order(models.Model):
    """
    Re-write to add check lists as a part of work flow
    """
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Cotizacion'),
        ('sent', 'Cotizacion Enviada'),
        ('sale', 'Orden de Venta'),
        ('done', 'Bloqueado'),
        ('cancel', 'Cancelado'),
        ('anular', 'Anulada'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')
    
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
                    raise UserError(_('No puedes cancelar un Pedido de Venta que tenga cantidad entregada.'))
                if lines.qty_invoiced!=0:
                    raise UserError(_('No puedes cancelar un Pedido de Venta que tenga cantidad facturadas.'))    
        return super(sale_order, self).action_cancel()