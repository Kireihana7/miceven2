# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    pagos_obtenidos = fields.Boolean(string="Pagos obtenidos",default=False)

    def remover_pagos(self):
        for rec in self:
            pagos = rec.line_ids.filtered(lambda x: x.payment_id).mapped('payment_id.id')
            self.env['account.payment'].search([('id','in',pagos)]).write({'statement_id':False})
            rec.line_ids.filtered(lambda x: x.payment_id).unlink()
            rec.pagos_obtenidos = False
            rec.balance_end_real = rec.balance_end

    def obtener_pagos(self):
        for rec in self:
            payments = self.env['account.payment'].search([('state','=','posted'),('date','=',rec.date),('journal_id','=',rec.journal_id.id),('statement_id','=',False)])
            if not payments:
                raise UserError('No existen pagos para la fecha seleccionada')
            for payment in payments:
                ref = ""
                for invoice in payment.reconciled_bill_ids:
                    ref += invoice.name
                for invoice in payment.reconciled_invoice_ids:
                    ref += invoice.name
                if len(ref) == 0:
                    ref = payment.ref
                values = {
                    "date": payment.date,
                    "partner_id": payment.partner_id.id,
                    "amount": payment.amount,
                    "ref": ref,
                    'payment_id':payment.id,
                    "payment_ref": payment.name,
                    'manual_currency_exchange_rate':payment.manual_currency_exchange_rate,
                }
                if payment.journal_id.currency_id and payment.journal_id.currency_id != payment.company_id.currency_id:
                    values['amount_currency'] = payment.amount_ref
                    values['foreign_currency_id'] = payment.company_id.currency_id.id
                else:
                    values['amount_currency'] = payment.amount_ref
                    values['foreign_currency_id'] = payment.company_id.currency_id.parent_id.id
                if payment.payment_type == "outbound":
                    values["amount"] = -1 * payment.amount
                    values["amount_currency"] = -1 * values["amount_currency"]
                payment.statement_id = rec.id
                lines = [(0,0,values)]
                rec.write({'line_ids':lines})

            rec.balance_end_real = rec.balance_end
            rec.pagos_obtenidos = True

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    payment_id = fields.Many2one("account.payment")
