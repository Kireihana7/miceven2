# -*- coding: utf-8 -*-
from odoo import models, fields,api,_
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = "stock.move"

    productor = fields.Many2one('res.partner',string="Productor",tracking=True)
    zona_partner = fields.Many2one('partner.zone',string="Zona",tracking=True)