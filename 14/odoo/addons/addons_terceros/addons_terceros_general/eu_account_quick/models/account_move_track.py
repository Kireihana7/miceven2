# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_id  = fields.Many2one(track_visibility="always")
#     partner_shipping_id = fields.Many2one(track_visibility="always")
#     invoice_date  = fields.Date(track_visibility="always")
#     invoice_date_due = fields.Date(track_visibility="always")
#     invoice_payment_term_id = fields.Many2one(track_visibility="always")
#     cuerrency_id = fields.Many2one(track_visibility="always")
#     account_id = fields.Many2one(track_visibility="always")
#     analytic_account_id = fields.Many2one(track_visibility="always")
#     journal_id = fields.Many2one(track_visibility="always")
#     invoice_user_id =  fields.Many2one(track_visibility="always")
#     date = fields.Date(track_visibility="always")


# class AccountPayment(models.Model):
#     _inherit = 'account.payment'


#     payment_type = fields.Selection(track_visibility="always")
#     partner_type = fields.Selection(track_visibility="always")
#     partner_id = fields.Many2one(track_visibility="always")
#     communication = fields.Char(track_visibility="always")
#     cuerrency_id = fields.Many2one(track_visibility="always")
#     payment_date = fields.Date(track_visibility="always")
#     journal_id = fields.Many2one(track_visibility="always")
#     partner_bank_id = fields.Many2one(track_visibility="always")



