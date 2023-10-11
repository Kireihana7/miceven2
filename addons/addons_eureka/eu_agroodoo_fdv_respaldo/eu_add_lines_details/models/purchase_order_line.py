# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    categ_id = fields.Many2one(related='product_id.categ_id',store=True , string="Categoria de Producto")
    # UPDATE:
    custom_requisition_id = fields.Many2one(string='Requisición', compute="_compute_custom_requisition_id", store=True)
    invoice_status = fields.Selection([
            ('no', 'Nada para facturar'), 
            ('to invoice', 'Para facturar'),
            ('invoiced', 'Totalmente facturado'),
        ],
        string='Estado de facturación', 
        compute="_compute_invoice_status", 
        store=True
    )

    @api.depends('order_id.custom_requisition_id')
    def _compute_custom_requisition_id(self):
        for rec in self:
            rec.custom_requisition_id = False
            if rec.order_id.custom_requisition_id:
                rec.custom_requisition_id = rec.order_id.custom_requisition_id

    @api.depends('order_id.invoice_status')
    def _compute_invoice_status(self):
        for rec in self:
            rec.invoice_status = False
            if rec.order_id.invoice_status:
                rec.invoice_status = rec.order_id.invoice_status
