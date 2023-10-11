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

from odoo import models, fields,api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    currency_id_dif = fields.Many2one(related="currency_id.parent_id",
        string="Moneda Secundaria",store=True)
   
    def inter_price(self):
        price_o=0.0
        price_u=0.0
        for record in self:
            for line in record.order_line:
                price_o=line.price_unit
                price_u=line.price_unit_ref
                line.price_unit=price_u
                line.price_unit_ref=price_u
            to_currency=record.currency_id_dif
            record.currency_id=to_currency

    @api.depends('amount_total','manual_currency_exchange_rate','currency_id')
    def _compute_amount_total_ref(self):
        for record in self:  
            record[("tax_today")] = 1
            record[("tax_today_two")] = 1
            record[("amount_total_ref")] = record.amount_total
            if record.manual_currency_exchange_rate != 0:
                record[("tax_today")]           = 1*record.manual_currency_exchange_rate
                record[("tax_today_two")]       = 1/record.manual_currency_exchange_rate                
                record[("amount_total_ref")]    = record['amount_total']*record.manual_currency_exchange_rate if record['currency_id'] == self.env.company.currency_id else record['amount_total']/record.manual_currency_exchange_rate
  
    tax_today           = fields.Float(store=True,readonly=True, default=0, compute="_compute_amount_total_ref", string="Tasa del Día $") 
    tax_today_two       = fields.Float(store=True,readonly=True, default=0, compute="_compute_amount_total_ref", string="Tasa del Día Bs") 
    amount_total_ref    = fields.Float(string='Monto Ref', store=True, readonly=True, tracking=4, default=0, compute="_compute_amount_total_ref")
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(20,10),default=lambda self: self.env.company.currency_id.parent_id.rate)
    amount_usd = fields.Float(string='Monto Inverso', compute='_compute_amount_usd',store=True)

    @api.depends('amount_total','amount_total_ref','currency_id','company_id')
    def _compute_amount_usd(self):
        for rec in self:
            rec.amount_usd = rec.amount_total if rec.currency_id != rec.company_id.currency_id else rec.amount_total_ref    