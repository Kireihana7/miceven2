# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    debit_move_parent_id = fields.Many2one(
        comodel_name='account.move',
        related="debit_move_id.move_id",
        store=True,
    )
    credit_move_parent_id = fields.Many2one(
        comodel_name='account.move',
        related="credit_move_id.move_id",
        store=True,
    )
    
    debit_move_payment_id = fields.Many2one(
        comodel_name='account.payment',
        related="debit_move_parent_id.payment_id",
        store=True,
    )
    credit_move_payment_id = fields.Many2one(
        comodel_name='account.payment',
        related="credit_move_parent_id.payment_id",
        store=True,
    )