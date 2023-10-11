# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_invoice_id  = fields.Many2one(track_visibility="always")
    partner_shipping_id = fields.Many2one(track_visibility="always")
    currency_id         = fields.Many2one(track_visibility="always")
    payment_term_id     = fields.Many2one(track_visibility="always")
    date_order          = fields.Datetime(track_visibility="always")
    analytic_account_id = fields.Many2one(track_visibility="always")