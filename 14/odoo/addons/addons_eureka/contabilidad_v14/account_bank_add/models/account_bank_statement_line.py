# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountBankState(models.Model):
    _inherit = 'account.bank.statement.line'

    should = fields.Monetary(
        string='Debe',
        #compute="_compute_tohave_should",
        default=0,
        readonly=True,
        compute="onchange_tohave_should",
        track_visibility="always",
    )
    tohave = fields.Monetary(
        string='Haber',
        #compute="_compute_tohave_should",
        default=0,
        readonly=True,
        compute="onchange_tohave_should",
        track_visibility="always",
    )

    @api.depends('amount')
    def onchange_tohave_should(self):
        for statement in self:
            if statement.amount >= 0:
                statement[("should")]=statement.amount
                statement[("tohave")]=0
            if statement.amount < 0:
                statement[("tohave")]=statement.amount
                statement[("should")]=0
