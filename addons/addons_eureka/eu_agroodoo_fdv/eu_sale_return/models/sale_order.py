# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    return_sale_ids = fields.One2many('sale.order.return','sale_id',string="Devoluciones Notificadas")
    return_sale_ids_count = fields.Integer(string="Cantidad de Devoluciones Notificadas",compute="_compute_return_sale_ids_count")

    @api.depends('return_sale_ids')
    def _compute_return_sale_ids_count(self):
        for rec in self:
            rec.return_sale_ids_count = len(rec.return_sale_ids)

    def open_sale_order_return(self):
        self.ensure_one()
        res = self.env.ref('eu_sale_return.open_sale_order_return')
        res = res.read()[0]
        res['domain'] = str([('sale_id', '=', self.id)])
        res['context'] = {'delete':False,'default_sale_id':self.id,'default_partner_id':self.partner_id.id}
        return res