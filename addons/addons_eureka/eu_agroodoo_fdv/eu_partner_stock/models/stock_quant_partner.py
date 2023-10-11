# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockQuantPartner(models.Model):
    _name = 'stock.quant.partner'
    _description = 'Inventario de Cliente'
    _order = 'create_date desc'
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre",default='/',readonly=True)
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users',string="Vendedor",default=lambda self: self.env.user,readonly=True)
    partner_id = fields.Many2one('res.partner',string="Cliente")
    product_id = fields.Many2one('product.product',string="Producto")
    quantity = fields.Float(string="Cantidad")
    uom_category_id = fields.Many2one('uom.category',related="product_id.category_id")
    uom_id = fields.Many2one('uom.uom',string="Unidad de Medida")
    visit_id = fields.Many2one('res.visit',string="Visita Relacionada")
    
    @api.model
    def create(self,vals):
        res = super(StockQuantPartner, self).create(vals)
        for rec in res:
            rec.name = self.env['ir.sequence'].next_by_code('stock.quant.partner.seq')
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.uom_id = rec.product_id.uom_id.id

    @api.constrains('partner_id','product_id')
    def _constrains_partner_quantity(self):
        for rec in self:
            if self.env['stock.quant.partner'].search([
                ('partner_id','=',rec.partner_id.id),
                ('product_id','=',rec.product_id.id),
                ('id','!=',rec.id)
                ],limit=1):
                raise UserError('Ya existe un registro para ese cliente con ese producto')