# -*- coding: utf-8 -*-

from odoo import models, fields,api,_
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    closed_receptions=fields.Boolean('cerrar por cantidades por recibir',tracking=True,copy=False)

    # partner_id          = fields.Many2one(track_visibility="always")
    # currency_id         = fields.Many2one(track_visibility="always")
    # product_id          = fields.Many2one(track_visibility="always")
    # product_uom         = fields.Many2one(track_visibility="always")
    # user_id             = fields.Many2one(track_visibility="always")
    # incoterm_id         = fields.Many2one(track_visibility="always")
    # date_order          = fields.Datetime(track_visibility="always")
    # analytic_account_id = fields.Many2one(track_visibility="always")
    # date_planned        = fields.Datetime(track_visibility="always")
    def close_po(self):
        for rec in self:
            rec.closed_receptions=True
            rec.message_post(
                        subject=(_("Cerrado para recepciones!")),
                        body="Este usuario a cerrado las recepciones para esta orden",
                        message_type='comment')
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    @api.depends('product_qty','qty_received','order_id','order_id.closed_receptions','order_id.invoice_status','write_date','name')
    def _compute_cantidad_por_recibir(self):
        for rec in self:
            rec.cantidad_por_recibir = rec.product_qty - rec.qty_received
            if rec.order_id.closed_receptions:
                rec.cantidad_por_recibir=0

    cantidad_por_recibir = fields.Float(string="Cantidad por Recibir",compute="_compute_cantidad_por_recibir",store=True,copy=False)

class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process_cancel_backorder(self):
        res = super(StockBackorderConfirmation, self).process_cancel_backorder()
        for rec in self:
            compras = rec.pick_ids.mapped('move_ids_without_package.purchase_line_id')
            for c in compras:
                c.cantidad_por_recibir = 0
            for cp in compras.mapped('order_id'):
                cp.closed_receptions = True
        return res
