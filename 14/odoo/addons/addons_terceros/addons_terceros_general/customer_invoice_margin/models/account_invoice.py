# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    margin_amount = fields.Float(compute='_get_average_margin_percentage', string='Margin Amount')
    margin_percentage = fields.Float(compute='_get_average_margin_percentage', string='Margin Percentage')

    @api.depends('invoice_line_ids','invoice_line_ids.quantity','invoice_line_ids.price_unit', 'invoice_line_ids.discount')
    def _get_average_margin_percentage(self):
        sale_price = discount = cost = margin_amount = 0.0
        line_cost = line_margin_amount = margin_percentage = 0.0
        for record in self:
            if record.invoice_line_ids:
                for line in record.invoice_line_ids:
                    sale_price = line.price_unit * line.quantity
                    discount = (sale_price * line.discount)/100
                    cost = line.product_id.standard_price * line.quantity
                    line_cost += cost
                    margin_amount = (sale_price - discount) - cost
                    line_margin_amount += margin_amount
                if line_cost:
                    margin_percentage = (line_margin_amount / line_cost) * 100
                else:
                    margin_percentage = 100
                record.margin_amount = line_margin_amount
                record.margin_percentage = round(margin_percentage,2)
            else:
                record.margin_amount = ''
                record.margin_percentage = ''

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        if 'margin_percentage' not in fields and 'margin_amount' not in fields:
            return super(AccountMove, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(AccountMove, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['margin_percentage'] = (sum(quant.margin_percentage for quant in quants) / float(len(quants)))
                group['margin_amount'] = sum(quant.margin_amount for quant in quants)

        return res        

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    margin_percentage = fields.Float(compute='_get_total_percentage', string='Margin Percentage')

    @api.depends('quantity','price_unit', 'discount')
    def _get_total_percentage(self):
        sale_price = discount = cost = margin_amount = margin_percentage = 0.0
        for record in self:
            if record.product_id:
                sale_price = record.price_unit * record.quantity
                discount = (sale_price*record.discount)/100
                cost = record.product_id.standard_price * record.quantity
                margin_amount = (sale_price - discount) - cost
                if cost:
                    margin_percentage = (margin_amount / cost) * 100 
                else:
                    margin_percentage = 100 
                record.margin_percentage = round(margin_percentage,2)
            else:
                record.margin_percentage = ''

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        if 'margin_percentage' not in fields :
            return super(AccountMoveLine, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(AccountMoveLine, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['margin_percentage'] = (sum(quant.margin_percentage for quant in quants) / float(len(quants)))
        return res