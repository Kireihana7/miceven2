# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.osv.expression import expression


class SellerDelayReport(models.Model):
    _name = "seller.delay.report"
    _description = "Seller Delay Report"
    _auto = False

    partner_id = fields.Many2one('res.partner', 'Vendedor', readonly=True)
    product_id = fields.Many2one('product.product', 'Producto', readonly=True)
    category_id = fields.Many2one('product.category', 'Categoria de Producto', readonly=True)
    date = fields.Datetime('Fecha Efectiva', readonly=True)
    qty_total = fields.Float('Cantidad Total', readonly=True)
    qty_on_time = fields.Float('Cantidad a Tiempo', readonly=True)
    on_time_rate_sale = fields.Float('Tasa de Entrega a Tiempo', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'seller_delay_report')
        self.env.cr.execute("""
CREATE OR replace VIEW seller_delay_report AS(
SELECT m.id                     AS id,
       m.date                   AS date,
       m.sale_line_id           AS sale_line_id,
       m.product_id             AS product_id,
       Min(pc.id)               AS category_id,
       Min(po.partner_id)       AS partner_id,
       Sum(pol.product_uom_qty) AS qty_total,
       Sum(CASE
             WHEN (so.commitment_date::date >= m.date::date) THEN ml.qty_done
             ELSE 0
           END)                 AS qty_on_time
FROM   stock_move m
       JOIN stock_move_line ml
         ON m.id = ml.move_id
       JOIN sale_order_line pol
         ON pol.id = m.sale_line_id
       JOIN sale_order po
         ON po.id = pol.order_id
       JOIN product_product p
         ON p.id = m.product_id
       JOIN product_template pt
         ON pt.id = p.product_tmpl_id
       JOIN product_category pc
         ON pc.id = pt.categ_id
        JOIN sale_order so
        ON so.id = pol.order_id
WHERE  m.state = 'done'
GROUP  BY m.id
)""")

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'on_time_rate_sale' not in fields:
            res = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
            return res

        fields.remove('on_time_rate_sale')
        if 'qty_total' not in fields:
            fields.append('qty_total')
        if 'qty_on_time' not in fields:
            fields.append('qty_on_time')
        res = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group['qty_total'] == 0:
                on_time_rate_sale = 100
            else:
                on_time_rate_sale = group['qty_on_time'] / group['qty_total'] * 100
            group.update({'on_time_rate_sale': on_time_rate_sale})

        return res