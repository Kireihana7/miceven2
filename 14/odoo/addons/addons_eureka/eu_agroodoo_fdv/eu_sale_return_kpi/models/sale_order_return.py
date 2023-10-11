# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderReturn(models.Model):
    _inherit= 'sale.order.return'

    visit_id = fields.Many2one('res.visit',string="Visita relacionada")