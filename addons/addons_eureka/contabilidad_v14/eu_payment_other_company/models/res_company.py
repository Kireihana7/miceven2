# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    account_intercompany_id = fields.Many2one('account.account',string="Cuenta Contable InterCompany")
