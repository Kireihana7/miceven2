# -*- coding: utf-8 -*-
#######################################################

#   CorpoEureka - Innovation First!
#
#   Copyright (C) 2021-TODAY CorpoEureka (<https://www.corpoeureka.com>)
#   Author: CorpoEureka (<https://www.corpoeureka.com>)
#
#   This software and associated files (the "Software") may only be used (executed,
#   modified, executed after modifications) if you have pdurchased a vali license
#   from the authors, typically via Odoo Apps, or if you have received a written
#   agreement from the authors of the Software (see the COPYRIGHT file).
#
#   You may develop Odoo modules that use the Software as a library (typically
#   by depending on it, importing it and using its resources), but without copying
#   any source code or material from the Software. You may distribute those
#   modules under the license of your choice, provided that this license is
#   compatible with the terms of the Odoo Proprietary License (For example:
#   LGPL, MIT, or proprietary licenses similar to this one).
#
#   It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#   or modified copies of the Software.
#
#   The above copyright notice and this permission notice must be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

#   Responsable CorpoEureka: Jose Mazzei
##########################################################################-

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('price_unit','order_id.manual_currency_exchange_rate','currency_id')
    def _compute_price_unit_ref(self):
        for record in self:  
            record[("price_unit_ref")]  = record['price_unit']
            if record.display_type == False and record.order_id.manual_currency_exchange_rate != 0: 
                record[("price_unit_ref")]    = record['price_unit']*record.order_id.manual_currency_exchange_rate if record['currency_id'] == self.env.company.currency_id else record['price_unit']/record.order_id.manual_currency_exchange_rate
     
    @api.onchange('product_uom_qty','price_unit_ref')
    def onchange_product_id_ref(self):
        for record in self:  
            record._compute_price_unit_ref()
            record[("price_subtotal_ref")] = record.product_uom_qty * record.price_unit_ref

    @api.depends('price_unit_ref','product_uom_qty')
    def _compute_price_subtotal_ref(self):
        for record in self:  
            record[("price_subtotal_ref")]   = 0
            if record.display_type == False:
                record[("price_subtotal_ref")] = record.product_uom_qty * record.price_unit_ref

    # Campos para Calcular la MultiMoneda
    price_unit_ref     = fields.Float(string='Precio Ref', store=True,  readonly=True, compute='_compute_price_unit_ref', tracking=4, default=0, invisible="1",digits=(20,3))
    price_subtotal_ref = fields.Float(string='Subtotal Ref',store=True, readonly=True, default=0,compute='_compute_price_subtotal_ref',digits=(20,3))
    currency_id_dif = fields.Many2one(related="order_id.currency_id.parent_id",
    string="Moneda Secundaria", invisible="1")
    