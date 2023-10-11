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
from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    debit_partial_reconcile_ids = fields.One2many(
        "account.partial.reconcile", 
        "debit_move_payment_id",
        "Conciliación parcial debito",
        tracking=True,
    )
    credit_partial_reconcile_ids = fields.One2many(
        "account.partial.reconcile", 
        "credit_move_payment_id",
        "Conciliación parcial credito",
        tracking=True,
    )
    
    importe_na = fields.Monetary("Importa no Añadido (Sin factura)", compute="_compute_importa_na")

    @api.depends('move_id.line_ids.account_id.user_type_id.type','move_id.line_ids.amount_residual','currency_id')
    def _compute_importa_na(self):
        for move in self:
            amounts = move.move_id \
                .line_ids \
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')) \
                .mapped(lambda l: l.amount_residual if move.currency_id == self.env.company.currency_id else l.amount_residual_currency)

            move.importe_na = abs(amounts[0] if amounts else 0)

    @api.depends('amount','manual_currency_exchange_rate','currency_id')
    def _amount_all_usd(self):
        for record in self:
            record[("amount_ref")]       = record.amount
            record[("tasa_del_dia")]     = 1
            record[("tasa_del_dia_two")] = 1
            if record.manual_currency_exchange_rate != 0:
                record[("amount_ref")]    = record['amount']*record.manual_currency_exchange_rate if record['currency_id'] == self.env.company.currency_id else record['amount']/record.manual_currency_exchange_rate
                record[("tasa_del_dia")]     = 1*record.manual_currency_exchange_rate
                record[("tasa_del_dia_two")] = 1/record.manual_currency_exchange_rate

    #  Campos Nuevos para el calculo de la doble moneda
    currency_id_ref = fields.Many2one(related="currency_id.parent_id",
    string="Moneda Referencia", invisible="1",store=True)
    tasa_del_dia     = fields.Float(store=True,readonly=True, compute="_amount_all_usd", default=0, digits=(20,10)) 
    tasa_del_dia_two = fields.Float(store=True,readonly=True, compute="_amount_all_usd", default=0, digits=(20,10)) 
    amount_ref       = fields.Float(string='Monto Ref', store=True, readonly=True, compute='_amount_all_usd', tracking=4, default=0)
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(20,10),default=lambda self: self.env.company.currency_id.parent_id.rate)
    # Modificación de campo para predefinir la compañia
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company.id,)

    amount_usd = fields.Float(string='Monto Inverso', compute='_compute_amount_usd',store=True)
    amount_company_currency = fields.Float(string='Monto USD', compute='_compute_amount_usd',store=True)
    origin_invoice = fields.Many2one('account.move',string="Factura Origen",readonly=True)
    draft_initial = fields.Boolean(string="Creado en Borrador",default=False)
    ref_bank = fields.Char(string="Referencia (Memo)")
    
    def action_post(self):
        result = super(AccountPayment, self).action_post()
        for rec in self:
            if rec.origin_invoice and rec.draft_initial:
                if rec.move_id.state != 'posted':
                    rec.move_id._post(soft=False)
                invoice = rec.move_id.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

                origen =  rec.origin_invoice.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                #raise UserError(('invoice: id - %s, name %s . origen: id - %s, name %s')%(invoice.move_id.state,invoice.move_id.name,origen.move_id.state,origen.move_id.name))
                conciliados = (invoice + origen).reconcile()
        return result

    @api.depends('amount','amount_ref','currency_id','company_id')
    def _compute_amount_usd(self):
        for rec in self:
            rec.amount_usd = rec.amount if rec.currency_id != rec.company_id.currency_id else rec.amount_ref
            rec.amount_company_currency = rec.amount if rec.currency_id == rec.company_id.currency_id else rec.amount_ref

    def write(self,vals):
        res = super(AccountPayment,self).write(vals)
        for rec in self:
            rec.move_id.write({
                'manual_currency_exchange_rate': rec.manual_currency_exchange_rate,
                'active_manual_currency_rate': rec.active_manual_currency_rate,
            })
            rec.move_id._onchange_manual_currency_rate()
            for line in rec.move_id.line_ids:
                line._report_usd_fields()
        return res

    @api.depends('partner_id', 'company_id', 'payment_type','journal_id')
    def _compute_partner_bank_id(self):
        res = super(AccountPayment,self)._compute_partner_bank_id()
        ''' The default partner_bank_id will be the first available on the partner. '''
        for pay in self:
            bank_partner = False
            available_partner_bank_accounts = False
            pay.partner_bank_id = False
            if pay.payment_type == 'inbound' and pay.journal_id:
                pay.partner_bank_id = pay.journal_id.bank_account_id.id
            if pay.payment_type == 'outbound':
                bank_partner = pay.partner_id
            if bank_partner:
                available_partner_bank_accounts = bank_partner.bank_ids.filtered(lambda x: x.company_id in (False, pay.company_id))
            if available_partner_bank_accounts:
                if pay.partner_bank_id not in available_partner_bank_accounts:
                    pay.partner_bank_id = available_partner_bank_accounts[0]._origin

    def _synchronize_to_moves(self, changed_fields):
        result = super(AccountPayment, self)._synchronize_to_moves(changed_fields)
        for rec in self:
            rec.move_id.write({
                'ref_bank': rec.ref_bank,
            })
        return result
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    origin_invoice = fields.Many2one('account.move',string="Factura Origen",readonly=True)
    ref_bank = fields.Char(string="Referencia (Memo)")

    @api.model
    def default_get(self, fields):
        result = super(AccountPaymentRegister, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.move':
            return result
        move_id = self.env['account.move'].browse(self._context.get('active_ids')).filtered(lambda move: move.is_invoice(include_receipts=True))
        result.update({
            'origin_invoice':move_id[0].id,
            })
        return result

    def _create_payment_vals_from_wizard(self):
        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        result.update({
            'origin_invoice':self.origin_invoice.id,
            'ref_bank':self.ref_bank,
        })
        return result

    def _create_payments_draft(self):
        self.ensure_one()
        batches = self._get_batches()
        edit_mode = self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment)

        to_reconcile = []
        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            payment_vals_list = [payment_vals]
            to_reconcile.append(batches[0]['lines'])
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines': line,
                        })
                batches = new_batches

            payment_vals_list = []
            for batch_result in batches:
                payment_vals_list.append(self._create_payment_vals_from_batch(batch_result))
                to_reconcile.append(batch_result['lines'])

        payments = self.env['account.payment'].create(payment_vals_list)
        payments.write({'draft_initial':True})
        # If payments are made using a currency different than the source one, ensure the balance match exactly in
        # order to fully paid the source journal items.
        # For example, suppose a new currency B having a rate 100:1 regarding the company currency A.
        # If you try to pay 12.15A using 0.12B, the computed balance will be 12.00A for the payment instead of 12.15A.
        if edit_mode:
            for payment, lines in zip(payments, to_reconcile):
                # Batches are made using the same currency so making 'lines.currency_id' is ok.
                if payment.currency_id != lines.currency_id:
                    liquidity_lines, counterpart_lines, writeoff_lines = payment._seek_for_lines()
                    source_balance = abs(sum(lines.mapped('amount_residual')))
                    payment_rate = liquidity_lines[0].amount_currency / liquidity_lines[0].balance
                    source_balance_converted = abs(source_balance) * payment_rate

                    # Translate the balance into the payment currency is order to be able to compare them.
                    # In case in both have the same value (12.15 * 0.01 ~= 0.12 in our example), it means the user
                    # attempt to fully paid the source lines and then, we need to manually fix them to get a perfect
                    # match.
                    payment_balance = abs(sum(counterpart_lines.mapped('balance')))
                    payment_amount_currency = abs(sum(counterpart_lines.mapped('amount_currency')))
                    if not payment.currency_id.is_zero(source_balance_converted - payment_amount_currency):
                        continue

                    delta_balance = source_balance - payment_balance

                    # Balance are already the same.
                    if self.company_currency_id.is_zero(delta_balance):
                        continue

                    # Fix the balance but make sure to peek the liquidity and counterpart lines first.
                    debit_lines = (liquidity_lines + counterpart_lines).filtered('debit')
                    credit_lines = (liquidity_lines + counterpart_lines).filtered('credit')

                    payment.move_id.write({'line_ids': [
                        (1, debit_lines[0].id, {'debit': debit_lines[0].debit + delta_balance}),
                        (1, credit_lines[0].id, {'credit': credit_lines[0].credit + delta_balance}),
                    ]})

        return payments

    def action_create_payments_draft(self):
        self._create_payments_draft()

    def _create_payments(self):
        self.ensure_one()
        batches = self._get_batches()
        edit_mode = self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment)

        to_reconcile = []
        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            payment_vals_list = [payment_vals]
            to_reconcile.append(batches[0]['lines'])
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines': line,
                        })
                batches = new_batches

            payment_vals_list = []
            for batch_result in batches:
                payment_vals_list.append(self._create_payment_vals_from_batch(batch_result))
                to_reconcile.append(batch_result['lines'])

        payments = self.env['account.payment'].create(payment_vals_list)

        # If payments are made using a currency different than the source one, ensure the balance match exactly in
        # order to fully paid the source journal items.
        # For example, suppose a new currency B having a rate 100:1 regarding the company currency A.
        # If you try to pay 12.15A using 0.12B, the computed balance will be 12.00A for the payment instead of 12.15A.
        if edit_mode:
            for payment, lines in zip(payments, to_reconcile):
                # Batches are made using the same currency so making 'lines.currency_id' is ok.
                if payment.currency_id != lines.currency_id:
                    liquidity_lines, counterpart_lines, writeoff_lines = payment._seek_for_lines()
                    source_balance = abs(sum(lines.mapped('amount_residual')))
                    payment_rate = liquidity_lines[0].amount_currency / liquidity_lines[0].balance
                    source_balance_converted = abs(source_balance) * payment_rate

                    # Translate the balance into the payment currency is order to be able to compare them.
                    # In case in both have the same value (12.15 * 0.01 ~= 0.12 in our example), it means the user
                    # attempt to fully paid the source lines and then, we need to manually fix them to get a perfect
                    # match.
                    payment_balance = abs(sum(counterpart_lines.mapped('balance')))
                    payment_amount_currency = abs(sum(counterpart_lines.mapped('amount_currency')))
                    if not payment.currency_id.is_zero(source_balance_converted - payment_amount_currency):
                        continue

                    delta_balance = source_balance - payment_balance

                    # Balance are already the same.
                    if self.company_currency_id.is_zero(delta_balance):
                        continue

                    # Fix the balance but make sure to peek the liquidity and counterpart lines first.
                    debit_lines = (liquidity_lines + counterpart_lines).filtered('debit')
                    credit_lines = (liquidity_lines + counterpart_lines).filtered('credit')

                    payment.move_id.write({'line_ids': [
                        (1, debit_lines[0].id, {'debit': debit_lines[0].debit + delta_balance}),
                        (1, credit_lines[0].id, {'credit': credit_lines[0].credit + delta_balance}),
                    ]})

        for line in payments.move_id.line_ids:
            line._onchange_amount_currency_ref()
        payments.action_post()

        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
        for payment, lines in zip(payments, to_reconcile):

            # When using the payment tokens, the payment could not be posted at this point (e.g. the transaction failed)
            # and then, we can't perform the reconciliation.
            if payment.state != 'posted':
                continue

            payment_lines = payment.line_ids.filtered_domain(domain)
            for account in payment_lines.account_id:
                (payment_lines + lines)\
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    .reconcile()

        return payments