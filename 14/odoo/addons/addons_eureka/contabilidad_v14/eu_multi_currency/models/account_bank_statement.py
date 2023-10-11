# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    manual_currency_exchange_rate = fields.Float(string='Tasa Manual', digits=(20,10))

    @api.model
    def _prepare_counterpart_move_line_vals(self, counterpart_vals, move_line=None):
        res = super(AccountBankStatementLine,self)._prepare_counterpart_move_line_vals(counterpart_vals,move_line)

        tasa = self.manual_currency_exchange_rate
        tasa_pago = self.env['account.payment'].search([('ref','=',self.ref),('state','=','posted')],limit=1).manual_currency_exchange_rate or 0.0
        if self.move_id.state != 'posted':
            if tasa>0:
                self.move_id.manual_currency_exchange_rate = tasa
                self.move_id.apply_manual_currency_exchange = True
            elif tasa_pago >0:
                self.move_id.manual_currency_exchange_rate = tasa_pago
                self.move_id.apply_manual_currency_exchange = True
                self.manual_currency_exchange_rate = tasa_pago
            self.move_id.asiento_conciliacion = True
        return res