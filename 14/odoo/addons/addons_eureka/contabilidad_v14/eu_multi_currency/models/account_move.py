# -*- coding: utf-8 -*-
#######################################################

#   CorpoEureka - Innovation First!
#
#   Copyright (C) 2021-TODAY CorpoEureka (<https://www.corpoeureka.com>)
#   Author: CorpoEureka (<https://www.corpoeureka.com>)
#
#   This software and associated files (the "Software") may only be used (executed,
#   modified, executed after modifications) if you have pdurchased a vali license
#   from the authors, typically via Odoo Apps, or if you have received a written
#   agreement from the authors of the Software (see the COPYRIGHT file).
#
#   You may develop Odoo modules that use the Software as a library (typically
#   by depending on it, importing it and using its resources), but without copying
#   any source code or material from the Software. You may distribute those
#   modules under the license of your choice, provided that this license is
#   compatible with the terms of the Odoo Proprietary License (For example:
#   LGPL, MIT, or proprietary licenses similar to this one).
#
#   It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#   or modified copies of the Software.
#
#   The above copyright notice and this permission notice must be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

#   Responsable CorpoEureka: Jose Mazzei
##########################################################################-

from odoo import api, fields, models,_
from datetime import date
from json import dumps
import json

class AccountMove(models.Model):
    _inherit = 'account.move'


    ref_bank = fields.Char(string="Referencia (Conciliación)")

    @api.depends('amount_total','manual_currency_exchange_rate','currency_id')
    def _amount_all_usd(self):
        for record in self:
            record[("amount_ref")]    = record['amount_total']
            if record.manual_currency_exchange_rate != 0:
                #total = sum(record.mapped('line_ids').filtered(lambda line: line.debit >0 ).mapped('balance'))
                record[("amount_ref")]    = record['amount_total']*record.manual_currency_exchange_rate if record['currency_id'] == self.env.company.currency_id else record['amount_total']/record.manual_currency_exchange_rate
                record[("tasa_del_dia")]     = round(1*record.manual_currency_exchange_rate,4)
                record[("tasa_del_dia_two")] = round(1/record.manual_currency_exchange_rate,4)

    @api.depends('amount_untaxed','manual_currency_exchange_rate','currency_id')
    def _compute_subtotal(self):
        for record in self:
            record[("amount_untaxed_ref")]  = record.amount_untaxed
            if record.manual_currency_exchange_rate != 0 and record.company_id.currency_id.id == record.currency_id.id:
                record[("amount_untaxed_ref")]  = record['amount_untaxed']*record.manual_currency_exchange_rate
                
    @api.depends('amount_residual_signed','manual_currency_exchange_rate','currency_id')
    def _compute_residual_ref(self):
        for record in self:
            record[("amount_residual_signed_ref")] = abs(record['amount_residual'])
            if record.manual_currency_exchange_rate != 0:
                record[("amount_residual_signed_ref")] = abs(record['amount_residual'] * record.manual_currency_exchange_rate if self.env.company.currency_id == record.currency_id else record['amount_residual']/record.manual_currency_exchange_rate)

    def write(self,vals):
        #self._onchange_manual_currency_rate()
        res = super(AccountMove, self).write(vals)
        for lines in self.filtered(lambda x: not x.payment_id).line_ids:
            lines._onchange_amount_currency_ref()
        #for rec in self.filtered(lambda x: not x.payment_id and not x.asiento_conciliacion):
        #    if not rec.asiento_diferencial:
        #        rec.computar_impuesto()
        return res

    @api.model
    def create(self,vals):
        #self._onchange_manual_currency_rate()
        res = super(AccountMove, self).create(vals)
        for lines in res.filtered(lambda x: not x.payment_id).line_ids:
            lines._onchange_amount_currency_ref()
        #for rec in res.filtered(lambda x: not x.payment_id and not x.asiento_conciliacion):
        #    if not rec.asiento_diferencial:
        #        rec.computar_impuesto()
        
        return res

    def computar_impuesto(self):
        for rec in self:
            if not rec.line_ids.mapped('full_reconcile_id.exchange_move_id'):
                #amount_currency = abs(sum(rec.line_ids.filtered(lambda x: x.tax_line_id != False).mapped('amount_currency')))
                line_payables = rec.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable','payables'))
                if len(rec.line_ids.filtered(lambda x: x.tax_line_id and x.tax_line_id.amount >0))>0:
                    for line in rec.line_ids.filtered(lambda x: x.tax_line_id and x.tax_line_id.amount >0):
                        amount_total = round(abs(sum(rec.invoice_line_ids.filtered(lambda x: x.tax_ids != False).mapped('price_subtotal'))) * (line.tax_line_id.amount / 100),4)
                        #raise UserError(amount_total)
                        if amount_total != line.amount_currency:
                            # line_payables.with_context(check_move_validity=False).write({
                            # 'debit': line_payables['debit'] - line.debit if line.debit > 0 else 0.0,
                            # 'credit': line_payables['credit'] - line.credit if line.credit > 0 else 0.0,
                            # })
                            #line.amount_currency = amount_total if line.debit > 0 else -amount_total
                            if rec.currency_id != self.env.company.currency_id:
                                diferencia = round(amount_total / rec.manual_currency_exchange_rate,4) - abs(line.balance) 
                                #raise UserError(('Diferencia moneda diferente: %s') %(diferencia))
                                line.with_context(check_move_validity=False).write({
                                    'debit':  round((amount_total / rec.manual_currency_exchange_rate),4) if line.debit > 0 else 0.0,
                                    'credit': round((amount_total / rec.manual_currency_exchange_rate),4) if line.credit > 0 else 0.0,
                                    'amount_currency':amount_total if line.debit > 0 else -amount_total,
                                })
                                line_payables.with_context(check_move_validity=False).write({
                                    'debit': abs((line_payables['debit'] + diferencia)) if line_payables['debit'] > 0 else 0.0,
                                    'credit': abs((line_payables['credit'] + diferencia)) if line_payables['credit'] > 0 else 0.0,
                                    'amount_currency':abs((abs(line_payables['balance']) + diferencia) * rec.manual_currency_exchange_rate) if line_payables['debit'] > 0 else -abs((abs(line_payables['balance']) + diferencia) * rec.manual_currency_exchange_rate),
                                })
                            else:
                                diferencia = round(amount_total,4) - abs(line.balance) 
                                #raise UserError(('Diferencia misma moneda: %s') %(diferencia))
                                line.with_context(check_move_validity=False).write({
                                    'debit': amount_total if line.debit > 0 else 0.0,
                                    'credit': amount_total if line.credit > 0 else 0.0,
                                    'amount_currency':amount_total if line.debit > 0 else -amount_total,
                                })
                                line_payables.with_context(check_move_validity=False).write({
                                    'debit': abs(round((line_payables['debit'] + diferencia),4)) if line_payables['debit'] > 0 else 0.0,
                                    'credit': abs(round((line_payables['credit'] + diferencia),4)) if line_payables['credit'] > 0 else 0.0,
                                    'amount_currency':abs((abs(line_payables['balance']) + diferencia)) if line_payables['debit'] > 0 else -abs((abs(line_payables['balance']) + diferencia)),
                                })

    #  Campos Nuevos para el calculo de la doble moneda
    tasa_del_dia                = fields.Float(store=True,readonly=True, compute="_amount_all_usd", default=0, digits=(20,10),string="Tasa del Día $") 
    tasa_del_dia_two            = fields.Float(store=True,readonly=True, compute="_amount_all_usd", default=0, digits=(20,10),string="Tasa del Día Bs") 
    amount_ref                  = fields.Float(string='Monto Ref', store=True, readonly=True, compute='_amount_all_usd', tracking=4, default=0)
    amount_untaxed_ref          = fields.Float(string='Sub Total Ref',store=True,readonly=True,compute='_compute_subtotal',tracking=4,default=0)
    amount_residual_signed_ref  = fields.Float(string='Imp Adeudado Ref',readonly=True,compute='_compute_residual_ref',tracking=4,default=0,store=True)
    currency_id_dif             = fields.Many2one(related="currency_id.parent_id",string="Moneda Referencia",)
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(20,10),default=lambda self: self.env.company.currency_id.parent_id.rate)
    manual_currency_exchange_rate_inv = fields.Float(string='Tasa Excel', digits=(20,10))
    amount_usd = fields.Float(string="Monto Inverso",compute="_compute_amount_usd",store=True)
    asiento_conciliacion = fields.Boolean(string="Asiento Conciliación",default=False)
    asiento_diferencial = fields.Boolean(string="Asiento Diferencial",default=False)

    @api.depends('amount_total','amount_ref','currency_id','company_id')
    def _compute_amount_usd(self):
        for rec in self:
            rec.amount_usd = rec.amount_total if rec.currency_id != rec.company_id.currency_id else rec.amount_ref

    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('move_id.state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')

            for line in self.env['account.move.line'].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    #amount = move.company_currency_id._convert(
                    #    abs(line.amount_residual),
                    #    move.currency_id,
                    #    move.company_id,
                    #    line.date,
                    #)
                    amount = abs(line.amount_residual) * move.manual_currency_exchange_rate if move.currency_id != self.env.company.currency_id else abs(line.amount_residual)

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.move_id.name,
                    'journal_name': str(line.move_id.ref_bank or '') + ' - ' + str(line.ref or line.move_id.name) + ' - ' + str(line.move_id.date) ,
                    'amount': amount,
                    'currency': move.currency_id.symbol,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'position': move.currency_id.position,
                    'digits': [69, move.currency_id.decimal_places],
                    'payment_date': fields.Date.to_string(line.date),
                })

            if not payments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
            move.invoice_has_outstanding = True