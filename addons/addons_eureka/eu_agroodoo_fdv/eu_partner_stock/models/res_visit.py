# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResVisit(models.Model):
    _inherit = 'res.visit'

    stock_inventory_ids = fields.One2many('stock.quant.partner','visit_id',string="Inventario de Cliente")
    stock_inventory_ids_count = fields.Integer(string="Inventario de Cliente Realizado",compute="_compute_stock_quant_partner_ids_count")

    @api.depends('stock_inventory_ids')
    def _compute_stock_quant_partner_ids_count(self):
        for rec in self:
            rec.stock_inventory_ids_count = len(rec.stock_inventory_ids)

    def open_stock_quant_partner(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError('Debes seleccionar un cliente primero')
        res = self.env.ref('eu_partner_stock.open_stock_quant_partner')
        res = res.read()[0]
        res['domain'] = str([('partner_id', '=', self.partner_id.id)])
        res['context'] = {'delete':False,'default_visit_id':self.id,'default_partner_id':self.partner_id.id}
        return res