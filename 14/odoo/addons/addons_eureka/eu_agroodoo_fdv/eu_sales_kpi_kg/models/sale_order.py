# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time, datetime
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    visit_id = fields.Many2one("res.visit", "Visita", tracking=True)

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res:
            if rec.sudo().visit_id:
                rec.sudo().visit_id.sale_order_id = rec.id
                self.env['res.traceability'].sudo().search([('sale_visii', '=', rec.visit_id.id)]).sudo().write({'sale_order':rec.id})
    
        return res
    
    def action_confirm(self):
        super().action_confirm()
        if self.sudo().visit_id:

            self.env['res.traceability'].sudo().search([('sale_visii', '=', self.visit_id.id)]).sudo().write({'create_date_so':datetime.datetime.today()})
         
           
    

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({
            'sale_id': self.id,
            })
        return result
