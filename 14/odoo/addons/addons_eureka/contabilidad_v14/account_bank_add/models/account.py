# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountBankState(models.Model):
    _inherit = 'account.bank.statement'
    
    should = fields.Monetary(
        string='Debe',
        #compute="_compute_tohave_should",
        default=0,
        readonly=True,
        compute="_compute_tohave_should",
        track_visibility="always",
    )
    tohave = fields.Monetary(
        string='Haber',
        #compute="_compute_tohave_should",
        default=0,
        readonly=True,
        compute="_compute_tohave_should",
        track_visibility="always",
    )

    @api.depends('line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real','currency_id')
    def _compute_tohave_should(self):
        for statement in self:
            statement[("should")]=0
            statement[("tohave")]=0
            for line in statement.line_ids:
                if line.amount >0:
                    statement[("should")] = statement[("should")] + line.amount
                if line.amount <0:
                    statement[("tohave")] = statement[("tohave")] + line.amount
    