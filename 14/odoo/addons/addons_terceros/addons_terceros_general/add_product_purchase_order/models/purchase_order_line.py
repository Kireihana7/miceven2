# -*- coding: utf-8 -*-
from odoo import models, fields,api,_
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    tipo_saco = fields.Many2one('product.saco',string="Tipo de Saco") 
    qty_saco = fields.Float(string="Cantidad de Saco")
    qty_bruto = fields.Float(string="Peso Bruto")
    qty_tara = fields.Float(string="Peso Tara",compute="_compute_qty_tara",store=True)
    precio_quintal = fields.Float(string="Precio Quintal")
    precio_kg = fields.Float(string="Precio KG",compute="_compute_qty_tara",store=True)
    lot_id = fields.Many2one('stock.production.lot',string="Tipo")
    precio_caleta = fields.Float(string="Precio Caleta",compute="_compute_qty_tara",store=True)
    precio_sin_caleta = fields.Float(string="Precio sin Caleta",compute="_compute_qty_tara",store=True)
    con_caleta = fields.Boolean(string="Con Caleta",default=True,store=True)
    productor = fields.Many2one('res.partner',string="Productor",tracking=True,related="order_id.productor")
    zona_partner = fields.Many2one('partner.zone',string="Zona",tracking=True,related="order_id.zona_partner")

    @api.depends('tipo_saco','qty_saco','precio_quintal','precio_kg','precio_caleta','qty_bruto','con_caleta')
    def _compute_qty_tara(self):
        for rec in self:
            rec.qty_tara = 0
            #rec.price_unit = 0
            rec.precio_caleta = 0
            #rec.product_qty = 0
            precio_caleta = 0
            rec.precio_kg = 0
            rec.precio_sin_caleta = 0
            rec.qty_tara = (rec.qty_saco * rec.tipo_saco.peso)
            if rec.tipo_saco and rec.qty_saco:
                precio_caleta = rec.precio_caleta = rec.tipo_saco.precio * rec.qty_saco
            if rec.qty_saco and rec.qty_bruto and rec.tipo_saco:
                rec.product_qty = rec.qty_bruto - (rec.qty_saco * rec.tipo_saco.peso)
            if rec.tipo_saco and rec.precio_quintal != 0 and rec.precio_caleta !=0:
                rec.price_unit = rec.precio_kg = (rec.precio_quintal / 46 ) - (precio_caleta / rec.product_qty)
            if rec.tipo_saco and rec.precio_quintal != 0 and not rec.con_caleta:
                rec.price_unit = rec.precio_kg = (rec.precio_quintal / 46 )

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super(PurchaseOrderLine,self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        res.update({
            'productor': self.productor.id,
            'zona_partner': self.zona_partner.id,
        })
        return res