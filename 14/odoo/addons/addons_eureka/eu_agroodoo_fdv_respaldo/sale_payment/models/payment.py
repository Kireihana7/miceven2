# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    sale_id = fields.Many2one(
        'sale.order',
        string='SO (Venta)',
        copy=False,
    )
    sale_id_status = fields.Selection(related="sale_id.state",string="Estatus de la SO")
    sale_id_status_invoice = fields.Char(related="sale_id.invoice_ids.name",string="Factura de la SO")
    sale_id_status_invoice_s  = fields.Selection(related="sale_id.invoice_ids.state",string="Estado Factura de la SO")

    sale_identify = fields.Char(
        string='ID de Presupuesto',
        copy=False,
    )

    currency_id_so = fields.Many2one(related="sale_id.currency_id", 
        string="Divisa de Referencia",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1), invisible=True,store=True)

    monto_padre_so = fields.Monetary(related="sale_id.amount_total",string="Monto de la SO (Venta)",store=True)
    @api.onchange('sale_id')
    def set_sale_indetify(self):
        for rec in self:
            if rec.sale_id.id:
                rec.sale_identify   = rec.sale_id.id
                rec.partner_id      = rec.sale_id.partner_id
                rec.ref   = rec.sale_id.name
                rec.currency_id_so  = rec.sale_id.currency_id
                rec.monto_padre_so  = rec.sale_id.amount_total

