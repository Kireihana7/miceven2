# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.advanced.payment'
    
    purchase_id = fields.Many2one(
        'purchase.order',
        string='PO (Compra)',
        copy=False,
    )
    purchase_id_status = fields.Selection(related="purchase_id.state",string="Estatus de la PO")
    purchase_id_status_invoice = fields.Char(related="purchase_id.invoice_ids.name",string="Factura de la PO")
    purchase_id_status_invoice_s  = fields.Selection(related="purchase_id.invoice_ids.state",string="Estado Factura de la PO")
    purchase_identify = fields.Char(
        string='ID de Presupuesto',
        copy=False,
    )

    currency_id_po = fields.Many2one(related="purchase_id.currency_id", 
        string="Divisa de Referencia",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1), invisible=True,store=True)

    monto_padre = fields.Monetary(related="purchase_id.amount_total",string="Monto de la PO (Compra)",store=True)

    @api.onchange('purchase_id')
    def set_purchase_indetify(self):
        for rec in self:
            if rec.purchase_id.id:
                rec.purchase_identify = rec.purchase_id.id
                rec.partner_id        = rec.purchase_id.partner_id
                rec.ref               = rec.purchase_id.name
                rec.currency_id_po    = rec.purchase_id.currency_id
                rec.monto_padre       = rec.purchase_id.amount_total
