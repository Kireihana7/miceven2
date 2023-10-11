# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime,date
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    # def create_invoices(self):
    #     res = super(SaleAdvancePaymentInv, self).create_invoices()
        
    #     sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        
    #     for order in sale_orders:
    #         salestarget_id =self.env['saletarget.saletarget'].search([
    #                 ('sales_person_id','=', order.user_id.id),
    #                 ('state','in', ['open']),
    #                 ],order="id",limit=1)
    #         if salestarget_id:
    #             if order.date_order.date() >= salestarget_id.start_date and order.date_order.date() <= salestarget_id.end_date:
    #                 for order_line in order.order_line:
    #                     for sale_line in salestarget_id.target_line_ids:
    #                         if order_line.product_id == sale_line.product_id:
    #                             achieve_quantity = sale_line.achieve_quantity + order_line.qty_invoiced
    #                             sale_line.write({'achieve_quantity': achieve_quantity})
    #                 salestarget_id.update({
    #                     #'target_achieve':'Sale Order Confirm',
    #                     'target_achieve':'Invoice Created',
    #                     'partner_id': order.partner_id.id
    #                 })
    #     return res
    

class AccountMove(models.Model):
    _inherit="account.move"

    saletarget_id = fields.Many2one('saletarget.saletarget', string='Objetivo de Venta', readonly=True)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        so_ids = self.mapped('invoice_line_ids').mapped('sale_line_ids').mapped('order_id')
        #sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for order in so_ids:
            salestarget_id =self.env['saletarget.saletarget'].search([
                    ('sales_person_id','=', order.user_id.id),
                    ('state','=', 'open'),
                    ],order="id",limit=1)
            if salestarget_id:
                self.write({'saletarget_id':salestarget_id.id})
                if order.date_order.date() >= salestarget_id.start_date and order.date_order.date() <= salestarget_id.end_date:
                    for order_line in order.order_line:
                        for sale_line in salestarget_id.target_line_ids:
                            if order_line.product_id == sale_line.product_id:
                                #raise UserError('hola')
                                achieve_quantity = sale_line.achieve_quantity + order_line.qty_invoiced
                                #achieve_quantity = 10
                                sale_line.write({'achieve_quantity': achieve_quantity})
                    salestarget_id.update({
                        #'target_achieve':'Sale Order Confirm',
                        'target_achieve':'Invoice Confirm',
                        'partner_id': order.partner_id.id
                    })
        return res

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        so_ids = self.mapped('invoice_line_ids').mapped('sale_line_ids').mapped('order_id')
        #sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for order in so_ids:
            salestarget_id =self.env['saletarget.saletarget'].search([
                    ('sales_person_id','=', order.user_id.id),
                    ('state','=', 'open'),
                    ],order="id",limit=1)
            if salestarget_id:
                self.write({'saletarget_id':salestarget_id.id})
                if order.date_order.date() >= salestarget_id.start_date and order.date_order.date() <= salestarget_id.end_date:
                    #raise UserError(order.date_order.date())
                    for order_line in order.order_line:
                        for sale_line in salestarget_id.target_line_ids:
                            if order_line.product_id == sale_line.product_id:
                                achieve_quantity = sale_line.achieve_quantity - order_line.qty_invoiced
                                #achieve_quantity = 10
                                sale_line.write({'achieve_quantity': achieve_quantity})
                    salestarget_id.update({
                        #'target_achieve':'Sale Order Confirm',
                        'target_achieve':'Invoice Draft',
                        'partner_id': order.partner_id.id
                    })
        return res

        

class SaleOrder(models.Model):
    _inherit="sale.order"

    saletarget_id = fields.Many2one('saletarget.saletarget', string='Objetivo de Venta', readonly=True)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            salestarget_id =self.env['saletarget.saletarget'].search([
                    ('sales_person_id','=', order.user_id.id),
                    ('state','in', ['open']),
                    ],order="id",limit=1)
            if salestarget_id:
                order.saletarget_id = salestarget_id.id
                if order.date_order.date() >= salestarget_id.start_date and order.date_order.date() <= salestarget_id.end_date:
                    for order_line in order.order_line:
                        for sale_line in salestarget_id.target_line_ids:
                            if order_line.product_id == sale_line.product_id:
                                #raise UserError('hola')
                                cotizado = sale_line.cotizado + order_line.product_uom_qty
                                sale_line.write({'cotizado': cotizado})
                    #salestarget_id.update({
                    #    'target_achieve':'Sale Order Confirm',
                    #    'partner_id': order.partner_id.id
                    #})
        return res