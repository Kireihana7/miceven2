# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    moneda_pago = fields.Many2one('res.currency',string="Moneda del Pago")

    def just_one_data(self,order_line):
        objetos = {}
        for i in order_line:
            if objetos.get(i.product_id.id) != None :
                objetos[i.product_id.id][1] += i.product_qty
                objetos[i.product_id.id][4] += i.price_subtotal 
            else:
                #                            0         1            2                   3            4                  5           6              7            8
                objetos[i.product_id.id] = [i.name,i.product_qty,i.product_uom.name,i.price_unit,i.price_subtotal,i.price_total,i.price_unit,i.display_type,i.product_id.default_code]
        return objetos

