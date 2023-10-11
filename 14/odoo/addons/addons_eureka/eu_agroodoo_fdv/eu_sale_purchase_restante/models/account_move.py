# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def open_move_line_view(self):
        self.ensure_one()
        res = self.env.ref('account.action_account_moves_all_a')
        res = res.read()[0]
        res['domain'] = str([('move_id', '=', self.id)])
        return res