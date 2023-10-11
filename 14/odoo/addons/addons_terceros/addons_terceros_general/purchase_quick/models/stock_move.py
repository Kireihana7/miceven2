# -*- coding: utf-8 -*-

from odoo import models, fields,api
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.depends('product_uom_qty','quantity_done')
    def _compute_cantidad_por_recibir(self):
        for rec in self:
            rec.cantidad_por_recibir = rec.product_uom_qty - rec.quantity_done

    cantidad_por_recibir = fields.Float(string="Cantidad por Recibir",compute="_compute_cantidad_por_recibir",store=True)