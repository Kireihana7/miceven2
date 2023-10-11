# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from pytz import timezone
from odoo.exceptions import UserError

class AccountMoveStockRefund(models.Model):
    _name = 'account.move.stock.refund'
    _description = 'Notificación a Inventario'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre',
        index=True,
    )
    state = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('done', 'Realizada'),
        ], 'Estatus', default='pendiente', index=True, required=True, readonly=True, copy=False, tracking=True)
    invoice_id = fields.Many2one('account.move',string="Factura")
    partner_id = fields.Many2one('res.partner',string="Contacto")
    move_type = fields.Selection(related="invoice_id.move_type",string="Tipo de Factura",store=True)
    refund_id = fields.Many2one('account.move',string="Nota de Crédito")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always',readonly=True)
    purchase_ids = fields.Many2many('purchase.order',string="Compras Relacionadas")
    sale_ids = fields.Many2many('sale.order',string="Ventas Relacionadas")
    picking_ids = fields.Many2many('stock.picking',string="Pickings Relacionados")

    def button_done(self):
        for rec in self:
            rec.state = 'done'

    def button_pendiente(self):
        for rec in self:
            rec.state = 'pendiente'

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'
    
    def reverse_moves(self):
        res = super(AccountMoveReversal, self).reverse_moves()

        vals_notify = {
            'name':str(self.move_ids[0].name) + ' - ' + str(self.new_move_ids[0].name),
            'partner_id': self.move_ids[0].partner_id.id,
            'invoice_id': self.move_ids[0].id,
            'move_type': self.move_ids[0].move_type,
            'refund_id':self.new_move_ids[0].id,
            'sale_ids': self.move_ids.mapped('invoice_line_ids').mapped('sale_line_ids.order_id').ids or False,
            'purchase_ids':self.move_ids.mapped('invoice_line_ids').mapped('purchase_line_id.order_id').ids or False,
            'picking_ids':self.move_ids.mapped('invoice_line_ids').mapped('purchase_line_id.move_ids.picking_id').ids or self.move_ids.mapped('invoice_line_ids').mapped('sale_line_ids.move_ids.picking_id').ids  or False,
        }
        notify_id = self.env['account.move.stock.refund'].create(vals_notify)

        return res 