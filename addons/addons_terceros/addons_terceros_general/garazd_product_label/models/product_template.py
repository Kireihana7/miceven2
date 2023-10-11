# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"


    currency_id_ref = fields.Many2one('res.currency',string="Moneda Ref",
        default=lambda self: self.env['res.currency'].search(['|',('name', '=', 'VES'),('name', '=', 'VEF')], limit=1))

    @api.depends('currency_id_ref','list_price')
    def _compute_list_price_ref(self):
        for rec in self:
            rec.list_price_ref = rec.env.company.currency_id._convert(rec.list_price, rec.currency_id_ref, rec.env.company, fields.date.today())

    list_price_ref = fields.Float('Precio de Venta Ref',compute="_compute_list_price_ref")