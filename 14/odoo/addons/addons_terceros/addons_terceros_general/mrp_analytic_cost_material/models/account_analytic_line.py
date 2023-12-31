# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    stock_move_id = fields.Many2one(
        "stock.move",
        string="Related Stock Move",
    )
    manufacturing_order_id = fields.Many2one(
        "mrp.production",
        string="Related Manufacturing Order",
    )
