# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, datetime, time
from odoo.exceptions import UserError

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_line_ids = fields.One2many('sale.order.line', 'order_partner_id', string="Sales Lines")
    on_time_rate_sale = fields.Float(
        "On-Time Delivery Rate", compute='_compute_on_time_rate_sale',
        help="Durante los últimos 12 meses; el número de productos entregados a tiempo dividido por el número de productos pedidos.")

    @api.depends('sale_line_ids')
    def _compute_on_time_rate_sale(self):
        sale_lines = self.env['sale.order.line'].search([
            ('order_partner_id', 'in', self.ids),
            ('order_id.date_order', '>', fields.Date.today() - timedelta(365)),
            ('qty_delivered', '!=', 0),
        ]).filtered(lambda l: l.product_id.sudo().product_tmpl_id.type != 'service' and l.order_id.state in ['done', 'sale'] and l.order_id.commitment_date)
        partner_dict = {}

        for line in sale_lines:
            on_time, ordered = partner_dict.get(line.order_partner_id, (0, 0))
            ordered += line.product_uom_qty
            on_time += sum(line.mapped('move_ids').filtered(lambda m: m.state == 'done' and m.date.date() <= m.sale_line_id.order_id.commitment_date.date()).mapped('quantity_done'))

            partner_dict[line.order_partner_id] = (on_time, ordered)
        seen_partner = self.env['res.partner']
        for partner, numbers in partner_dict.items():
            seen_partner |= partner
            on_time, ordered = numbers
            partner.on_time_rate_sale = on_time / ordered * 100 if ordered else -1   # use negative number to indicate no data
        (self - seen_partner).on_time_rate_sale = -1


#on_time += sum(line.mapped('move_ids').filtered(lambda m: m.state == 'done' and m.date.date() <= m.sale_line_id.order_id.commitment_date.date()).mapped('quantity_done'))
