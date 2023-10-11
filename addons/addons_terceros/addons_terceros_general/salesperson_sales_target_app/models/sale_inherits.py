# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime,date

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        
        for order in sale_orders:
            salestarget_id =self.env['saletarget.saletarget'].search([
                    ('sales_person_id','=', order.user_id.id),
                    ('state','in', ['open']),
                    ],order="id",limit=1)
            if salestarget_id:
                if order.date_order.date() >= salestarget_id.start_date and order.date_order.date() <= salestarget_id.end_date:
                    for order_line in order.order_line:
                        for sale_line in salestarget_id.target_line_ids:
                            if order_line.product_id == sale_line.product_id:
                                achieve_quantity = sale_line.achieve_quantity + order_line.qty_invoiced
                                sale_line.write({'achieve_quantity': achieve_quantity})
                    salestarget_id.update({
                        #'target_achieve':'Sale Order Confirm',
                        'target_achieve':'Invoice Created',
                        'partner_id': order.partner_id.id
                    })
        return res

class SaleOrder(models.Model):
    _inherit="sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            salestarget_id =self.env['saletarget.saletarget'].search([
                    ('sales_person_id','=', order.user_id.id),
                    ('state','in', ['open']),
                    ],order="id",limit=1)
            if salestarget_id:
                if order.date_order.date() >= salestarget_id.start_date and order.date_order.date() <= salestarget_id.end_date:
                    for order_line in order.order_line:
                        for sale_line in salestarget_id.target_line_ids:
                            if order_line.product_id == sale_line.product_id:
                                cotizado = sale_line.cotizado + order_line.product_uom_qty
                                sale_line.write({'cotizado': cotizado})
                    #salestarget_id.update({
                    #    'target_achieve':'Sale Order Confirm',
                    #    'partner_id': order.partner_id.id
                    #})
        return res