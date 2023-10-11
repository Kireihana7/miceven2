# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderReturn(models.Model):
    _name = 'sale.order.return'
    _description = 'Retorno De Venta'
    _order = 'create_date desc'
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre",default='/',readonly=True)
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users',string="Vendedor",default=lambda self: self.env.user,readonly=True)
    note = fields.Char(string="Motivo de Devolución",required=True)
    sale_id = fields.Many2one('sale.order',string="Venta")    
    partner_id = fields.Many2one('res.partner',string="Cliente")
    product_id = fields.Many2one('product.product',string="Producto a devolver")
    quantity = fields.Float(string="Cantidad a Devolver")
    invoice_id = fields.Many2one('account.move',string="Factura relacionada")
    uom_category_id = fields.Many2one('uom.category',related="product_id.category_id")
    uom_id = fields.Many2one('uom.uom',string="Unidad de Medida")
    sica_image = fields.Binary('Guía SICA', attachment=True)    

    @api.model
    def create(self,vals):
        res = super(SaleOrderReturn, self).create(vals)
        for rec in res:
            if not rec.sale_id:
                rec.sale_id = self.env.context.get('active_id', False) or False
            rec.name = self.env['ir.sequence'].next_by_code('sale.order.return.seq')
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.uom_id = rec.product_id.uom_id.id