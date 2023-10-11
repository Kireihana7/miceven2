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
from odoo.exceptions import UserError
from datetime import date, timedelta

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('price_unit','move_id.manual_currency_exchange_rate','currency_id')
    def _compute_price_unit_ref(self):
        for record in self:
            record[("price_unit_ref")] = record['price_unit']
            if record.move_id.manual_currency_exchange_rate != 0 and record.display_type == False:
                record[("price_unit_ref")] = record['price_unit']*record.move_id.manual_currency_exchange_rate if record['currency_id'] == self.env.company.currency_id else record['price_unit']/record.move_id.manual_currency_exchange_rate

    @api.onchange('product_id','quantity','price_subtotal','move_id','move_id.manual_currency_exchange_rate')
    def onchange_product_id_ref(self):
        for record in self:  
            record._compute_price_unit_ref()
            record[("price_subtotal_ref")] = record.price_subtotal * record.move_id.manual_currency_exchange_rate

    @api.depends('price_unit_ref','quantity','price_subtotal','move_id','move_id.manual_currency_exchange_rate')
    def _compute_price_subtotal_ref(self):
        for record in self:
            record[("price_subtotal_ref")] = record[("price_subtotal")]
            if record.move_id.manual_currency_exchange_rate != 0 and record.display_type == False:  
                record[("price_subtotal_ref")] = record.price_subtotal * record.move_id.manual_currency_exchange_rate
    
    # @api.onchange('price_unit','price_total')
    # def _onchange_price_unit_ref(self):
    #     for rec in self:
    #         if rec.move_id:
    #             rec.move_id._onchange_manual_currency_rate()
    #             rec.move_id._onchange_currency()

    @api.onchange('currency_id')
    def _onchange_currency(self):
        for line in self:
            company = line.move_id.company_id

            if line.move_id.is_invoice(include_receipts=True):
                line._onchange_price_subtotal()
            elif not line.move_id.reversed_entry_id and not line.move_id.asiento_diferencial:
                balance = 0.0
                if line.currency_id != self.env.company.currency_id and line.manual_currency_exchange_rate != 0:
                    balance = line.amount_currency / line.move_id.manual_currency_exchange_rate
                if line.currency_id == self.env.company.currency_id:
                    balance = line.amount_currency
                line.debit = balance if balance > 0.0 else 0.0
                line.credit = -balance if balance < 0.0 else 0.0
            # if line.mapped('full_reconcile_id.exchange_move_id'):
            #     line.mapped('full_reconcile_id.exchange_move_id').button_draft()
            #     line.mapped('full_reconcile_id.exchange_move_id.line_ids').debit_usd = abs(line.amount_currency)
            #     line.mapped('full_reconcile_id.exchange_move_id.line_ids').credit_usd = abs(line.amount_currency)
            #     line.mapped('full_reconcile_id.exchange_move_id.line_ids').balance_usd = line.amount_currency
            #     line.mapped('full_reconcile_id.exchange_move_id.line_ids').debit =  0.0
            #     line.mapped('full_reconcile_id.exchange_move_id.line_ids').credit = 0.0
            #     line.mapped('full_reconcile_id.exchange_move_id.line_ids').balance = 0.0
    # Campos para Calcular la MultiMoneda
    price_unit_ref = fields.Float(string='Monto Ref', store=True,readonly=True, compute='_compute_price_unit_ref', tracking=4, default=0, invisible="1",digits=(20,4))
    price_subtotal_ref = fields.Float(string='Subtotal Ref',store=True, readonly=True, tracking=4, default=0,compute='_compute_price_subtotal_ref',digits=(20,4))
    currency_id_line = fields.Many2one(related="move_id.currency_id_dif",string="Moneda Referencia", invisible="1",store=True)
    company_id = fields.Many2one(related="move_id.company_id",store=True)
    invoice_date = fields.Date(related="move_id.invoice_date",store=True)

    # Añadir Multimoneda en Cuenta Analítica (Centro de Costos)
    def _prepare_analytic_line(self):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            an analytic account. This method is intended to be extended in other modules.
            :return list of values to create analytic.line
            :rtype list
        """
        super(AccountMoveLine, self)._prepare_analytic_line()
        result = []
        amount_usd= 0.0
        for move_line in self:
            amount = (move_line.credit or 0.0) - (move_line.debit or 0.0)
            if amount < 0:
                amount_usd=move_line.price_subtotal_ref * -1
            else:
                amount_usd=move_line.price_subtotal_ref
            default_name = move_line.name or (move_line.ref or '/' + ' -- ' + (move_line.partner_id and move_line.partner_id.name or '/'))
            result.append({
                'name': default_name,
                'date': move_line.date,
                'account_id': move_line.analytic_account_id.id,
                'tag_ids': [(6, 0, move_line._get_analytic_tag_ids())],
                'unit_amount': move_line.quantity,
                'product_id': move_line.product_id and move_line.product_id.id or False,
                'product_uom_id': move_line.product_uom_id and move_line.product_uom_id.id or False,
                'amount': amount,
                'amount_usd': amount_usd,
                'general_account_id': move_line.account_id.id,
                'ref': move_line.ref,
                'move_id': move_line.id,
                'user_id': move_line.move_id.invoice_user_id.id or self._uid,
                'partner_id': move_line.partner_id.id,
                'company_id': move_line.analytic_account_id.company_id.id or self.env.company.id,
            })
        return result

    # Añadir Multimoneda en Cuenta Analítica (Centro de Costos)
    def _prepare_analytic_distribution_line(self, distribution):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            analytic tags with analytic distribution.
        """
        super(AccountMoveLine, self)._prepare_analytic_distribution_line(distribution)
        amount_usd= 0.0
        self.ensure_one()
        amount = -self.balance * distribution.percentage / 100.0
        default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
        if amount < 0:
                amount_usd=self.price_subtotal_ref * -1
        else:
            amount_usd=self.price_subtotal_ref
        return {
            'name': default_name,
            'date': self.date,
            'account_id': distribution.account_id.id,
            'partner_id': self.partner_id.id,
            'tag_ids': [(6, 0, [distribution.tag_id.id] + self._get_analytic_tag_ids())],
            'unit_amount': self.quantity,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
            'amount': amount,
            'amount_usd': amount_usd,
            'general_account_id': self.account_id.id,
            'ref': self.ref,
            'move_id': self.id,
            'user_id': self.move_id.invoice_user_id.id or self._uid,
            'company_id': distribution.account_id.company_id.id or self.env.company.id,
        }

    debit_usd   = fields.Monetary('Debit Ref',default=0.0, currency_field='currency_id_line',compute="_report_usd_fields",store=True)
    credit_usd  = fields.Monetary('Credit Ref',default=0.0, currency_field='currency_id_line',compute="_report_usd_fields",store=True)
    balance_usd = fields.Monetary('Balance Ref',default=0.0, currency_field='currency_id_line',compute="_report_usd_fields",store=True)
    
    @api.depends('debit','credit','balance','move_id.manual_currency_exchange_rate','move_id.currency_id','move_id.asiento_diferencial')
    def _report_usd_fields(self):
        for rec in self:
            rec.debit_usd = 0 
            rec.credit_usd = 0 
            rec.balance_usd = 0
            if rec.move_id.currency_id != self.env.company.currency_id:
                if rec.debit != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.debit_usd = abs(rec.amount_currency)
                if rec.credit != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.credit_usd = abs(rec.amount_currency)
                if rec.balance != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.balance_usd = rec.amount_currency
            else:
                if rec.debit != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.debit_usd = rec.debit * rec.move_id.manual_currency_exchange_rate
                if rec.credit != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.credit_usd = rec.credit * rec.move_id.manual_currency_exchange_rate
                if rec.balance != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.balance_usd = rec.balance * rec.move_id.manual_currency_exchange_rate
            if rec.move_id.asiento_diferencial:
                rec.debit_usd = abs(rec.amount_currency) if rec.amount_currency > 0 else 0
                rec.credit_usd = abs(rec.amount_currency) if rec.amount_currency < 0 else 0
                rec.balance_usd = rec.amount_currency


    @api.onchange('amount_currency')
    def _onchange_amount_currency_ref(self):
        if not self.mapped('full_reconcile_id.exchange_move_id'):
            balance = 0 
            if self.env.company.currency_id == self.move_id.currency_id:
                balance = self.amount_currency 
            if self.env.company.currency_id != self.move_id.currency_id and self.manual_currency_exchange_rate !=0:
                balance = self.amount_currency / self.manual_currency_exchange_rate
             #balance = currency._convert(amount_currency, company.currency_id, company, date or fields.Date.context_today(self))
            if not self.matched_debit_ids and not self.matched_credit_ids and not self.move_id.asiento_diferencial:
                self.debit =  balance > 0.0 and balance or 0.0
                self.credit =  balance < 0.0 and -balance or 0.0
    
    def _prepare_reconciliation_partials(self): 
        ''' Prepare the partials on the current journal items to perform the reconciliation.
        /!\ The order of records in self is important because the journal items will be reconciled using this order.
        :return: A recordset of account.partial.reconcile.
        '''
        debit_lines = iter(self.filtered(lambda line: line.balance > 0.0 or line.amount_currency > 0.0))
        credit_lines = iter(self.filtered(lambda line: line.balance < 0.0 or line.amount_currency < 0.0))
        debit_line = None
        credit_line = None

        debit_amount_residual = 0.0
        debit_amount_residual_currency = 0.0
        credit_amount_residual = 0.0
        credit_amount_residual_currency = 0.0
        debit_line_currency = None
        credit_line_currency = None

        partials_vals_list = []

        while True:

            # Move to the next available debit line.
            if not debit_line:
                debit_line = next(debit_lines, None)
                if not debit_line:
                    break
                debit_amount_residual = debit_line.amount_residual

                if debit_line.currency_id:
                    debit_amount_residual_currency = debit_line.amount_residual_currency
                    debit_line_currency = debit_line.currency_id
                else:
                    debit_amount_residual_currency = debit_amount_residual
                    debit_line_currency = debit_line.company_currency_id

            # Move to the next available credit line.
            if not credit_line:
                credit_line = next(credit_lines, None)
                if not credit_line:
                    break
                credit_amount_residual = credit_line.amount_residual

                if credit_line.currency_id:
                    credit_amount_residual_currency = credit_line.amount_residual_currency
                    credit_line_currency = credit_line.currency_id
                else:
                    credit_amount_residual_currency = credit_amount_residual
                    credit_line_currency = credit_line.company_currency_id

            min_amount_residual = min(debit_amount_residual, -credit_amount_residual)
            has_debit_residual_left = not debit_line.company_currency_id.is_zero(debit_amount_residual) and debit_amount_residual > 0.0
            has_credit_residual_left = not credit_line.company_currency_id.is_zero(credit_amount_residual) and credit_amount_residual < 0.0
            has_debit_residual_curr_left = not debit_line_currency.is_zero(debit_amount_residual_currency) and debit_amount_residual_currency > 0.0
            has_credit_residual_curr_left = not credit_line_currency.is_zero(credit_amount_residual_currency) and credit_amount_residual_currency < 0.0

            if debit_line_currency == credit_line_currency:
                # Reconcile on the same currency.

                # The debit line is now fully reconciled because:
                # - either amount_residual & amount_residual_currency are at 0.
                # - either the credit_line is not an exchange difference one.
                if not has_debit_residual_curr_left and (has_credit_residual_curr_left or not has_debit_residual_left):
                    debit_line = None
                    continue

                # The credit line is now fully reconciled because:
                # - either amount_residual & amount_residual_currency are at 0.
                # - either the debit is not an exchange difference one.
                if not has_credit_residual_curr_left and (has_debit_residual_curr_left or not has_credit_residual_left):
                    credit_line = None
                    continue

                min_amount_residual_currency = min(debit_amount_residual_currency, -credit_amount_residual_currency)
                min_debit_amount_residual_currency = min_amount_residual_currency
                min_credit_amount_residual_currency = min_amount_residual_currency

            else:
                # Reconcile on the company's currency.

                # The debit line is now fully reconciled since amount_residual is 0.
                if not has_debit_residual_left:
                    debit_line = None
                    continue

                # The credit line is now fully reconciled since amount_residual is 0.
                if not has_credit_residual_left:
                    credit_line = None
                    continue

                min_debit_amount_residual_currency = credit_line.company_currency_id._convert(
                    min_amount_residual,
                    debit_line.currency_id,
                    credit_line.company_id,
                    credit_line.date,
                )
                min_debit_amount_residual_currency = min_amount_residual * credit_line.manual_currency_exchange_rate if debit_line.currency_id != self.env.company.currency_id else min_amount_residual 
                min_credit_amount_residual_currency = debit_line.company_currency_id._convert(
                    min_amount_residual,
                    credit_line.currency_id,
                    debit_line.company_id,
                    debit_line.date,
                )
                min_credit_amount_residual_currency = min_amount_residual * debit_line.manual_currency_exchange_rate if credit_line.currency_id != self.env.company.currency_id else min_amount_residual 
                

            debit_amount_residual -= min_amount_residual
            debit_amount_residual_currency -= min_debit_amount_residual_currency
            credit_amount_residual += min_amount_residual
            credit_amount_residual_currency += min_credit_amount_residual_currency

            partials_vals_list.append({
                'amount': min_amount_residual,
                'debit_amount_currency': min_debit_amount_residual_currency,
                'credit_amount_currency': min_credit_amount_residual_currency,
                'debit_move_id': debit_line.id,
                'credit_move_id': credit_line.id,
            })

        return partials_vals_list


    def _create_exchange_difference_move(self):
        ''' Create the exchange difference journal entry on the current journal items.
        :return: An account.move record.
        '''

        def _add_lines_to_exchange_difference_vals(lines, exchange_diff_move_vals):
            ''' Generate the exchange difference values used to create the journal items
            in order to fix the residual amounts and add them into 'exchange_diff_move_vals'.

            1) When reconciled on the same foreign currency, the journal items are
            fully reconciled regarding this currency but it could be not the case
            of the balance that is expressed using the company's currency. In that
            case, we need to create exchange difference journal items to ensure this
            residual amount reaches zero.

            2) When reconciled on the company currency but having different foreign
            currencies, the journal items are fully reconciled regarding the company
            currency but it's not always the case for the foreign currencies. In that
            case, the exchange difference journal items are created to ensure this
            residual amount in foreign currency reaches zero.

            :param lines:                   The account.move.lines to which fix the residual amounts.
            :param exchange_diff_move_vals: The current vals of the exchange difference journal entry.
            :return:                        A list of pair <line, sequence> to perform the reconciliation
                                            at the creation of the exchange difference move where 'line'
                                            is the account.move.line to which the 'sequence'-th exchange
                                            difference line will be reconciled with.
            '''
            journal = self.env['account.journal'].browse(exchange_diff_move_vals['journal_id'])
            to_reconcile = []

            for line in lines:

                exchange_diff_move_vals['date'] = max(exchange_diff_move_vals['date'], line.date)

                if not line.company_currency_id.is_zero(line.amount_residual):
                    # amount_residual_currency == 0 and amount_residual has to be fixed.

                    if line.amount_residual > 0.0:
                        exchange_line_account = journal.company_id.expense_currency_exchange_account_id
                    else:
                        exchange_line_account = journal.company_id.income_currency_exchange_account_id

                elif line.currency_id and not line.currency_id.is_zero(line.amount_residual_currency):
                    # amount_residual == 0 and amount_residual_currency has to be fixed.

                    if line.amount_residual_currency > 0.0:
                        exchange_line_account = journal.company_id.expense_currency_exchange_account_id
                    else:
                        exchange_line_account = journal.company_id.income_currency_exchange_account_id
                else:
                    continue

                sequence = len(exchange_diff_move_vals['line_ids'])
                exchange_diff_move_vals['line_ids'] += [
                    (0, 0, {
                        'name': _('Currency exchange rate difference'),
                        'debit': 0.0,
                        'credit':0.0,
                        'debit_usd': -line.amount_residual_currency if line.amount_residual_currency < 0.0 else 0.0,
                        'credit_usd': line.amount_residual_currency if line.amount_residual_currency > 0.0 else 0.0,
                        'amount_currency': -line.amount_residual_currency,
                        'account_id': line.account_id.id,
                        'currency_id': self.env.company.currency_id.parent_id.id,
                        'partner_id': line.partner_id.id,
                        'sequence': sequence,
                    }),
                    (0, 0, {
                        'name': _('Currency exchange rate difference'),
                        'debit': 0.0,
                        'credit':0.0,
                        'debit_usd': line.amount_residual_currency if line.amount_residual_currency > 0.0 else 0.0,
                        'credit_usd': -line.amount_residual_currency if line.amount_residual_currency < 0.0 else 0.0,
                        'amount_currency': line.amount_residual_currency,
                        'account_id': exchange_line_account.id,
                        'currency_id': self.env.company.currency_id.parent_id.id,
                        'partner_id': line.partner_id.id,
                        'sequence': sequence + 1,
                    }),
                ]

                to_reconcile.append((line, sequence))

            return to_reconcile

        def _add_cash_basis_lines_to_exchange_difference_vals(lines, exchange_diff_move_vals):
            ''' Generate the exchange difference values used to create the journal items
            in order to fix the cash basis lines using the transfer account in a multi-currencies
            environment when this account is not a reconcile one.

            When the tax cash basis journal entries are generated and all involved
            transfer account set on taxes are all reconcilable, the account balance
            will be reset to zero by the exchange difference journal items generated
            above. However, this mechanism will not work if there is any transfer
            accounts that are not reconcile and we are generating the cash basis
            journal items in a foreign currency. In that specific case, we need to
            generate extra journal items at the generation of the exchange difference
            journal entry to ensure this balance is reset to zero and then, will not
            appear on the tax report leading to erroneous tax base amount / tax amount.

            :param lines:                   The account.move.lines to which fix the residual amounts.
            :param exchange_diff_move_vals: The current vals of the exchange difference journal entry.
            '''
            for move in lines.move_id:
                account_vals_to_fix = {}

                move_values = move._collect_tax_cash_basis_values()

                # The cash basis doesn't need to be handle for this move because there is another payment term
                # line that is not yet fully paid.
                if not move_values or not move_values['is_fully_paid']:
                    continue

                # ==========================================================================
                # Add the balance of all tax lines of the current move in order in order
                # to compute the residual amount for each of them.
                # ==========================================================================

                for line in move_values['to_process_lines']:

                    vals = {
                        'currency_id': line.currency_id.id,
                        'partner_id': line.partner_id.id,
                        'tax_ids': [(6, 0, line.tax_ids.ids)],
                        'tax_tag_ids': [(6, 0, line._convert_tags_for_cash_basis(line.tax_tag_ids).ids)],
                        'debit': line.debit,
                        'credit': line.credit,
                    }

                    if line.tax_repartition_line_id:
                        # Tax line.
                        grouping_key = self.env['account.partial.reconcile']._get_cash_basis_tax_line_grouping_key_from_record(line)
                        if grouping_key in account_vals_to_fix:
                            debit = account_vals_to_fix[grouping_key]['debit'] + vals['debit']
                            credit = account_vals_to_fix[grouping_key]['credit'] + vals['credit']
                            balance = debit - credit

                            account_vals_to_fix[grouping_key].update({
                                'debit': balance if balance > 0 else 0,
                                'credit': -balance if balance < 0 else 0,
                                'tax_base_amount': account_vals_to_fix[grouping_key]['tax_base_amount'] + line.tax_base_amount,
                            })
                        else:
                            account_vals_to_fix[grouping_key] = {
                                **vals,
                                'account_id': line.account_id.id,
                                'tax_base_amount': line.tax_base_amount,
                                'tax_repartition_line_id': line.tax_repartition_line_id.id,
                            }
                    elif line.tax_ids:
                        # Base line.
                        account_to_fix = line.company_id.account_cash_basis_base_account_id
                        if not account_to_fix:
                            continue

                        grouping_key = self.env['account.partial.reconcile']._get_cash_basis_base_line_grouping_key_from_record(line, account=account_to_fix)

                        if grouping_key not in account_vals_to_fix:
                            account_vals_to_fix[grouping_key] = {
                                **vals,
                                'account_id': account_to_fix.id,
                            }
                        else:
                            # Multiple base lines could share the same key, if the same
                            # cash basis tax is used alone on several lines of the invoices
                            account_vals_to_fix[grouping_key]['debit'] += vals['debit']
                            account_vals_to_fix[grouping_key]['credit'] += vals['credit']

                # ==========================================================================
                # Subtract the balance of all previously generated cash basis journal entries
                # in order to retrieve the residual balance of each involved transfer account.
                # ==========================================================================

                cash_basis_moves = self.env['account.move'].search([('tax_cash_basis_move_id', '=', move.id)])
                for line in cash_basis_moves.line_ids:
                    grouping_key = None
                    if line.tax_repartition_line_id:
                        # Tax line.
                        grouping_key = self.env['account.partial.reconcile']._get_cash_basis_tax_line_grouping_key_from_record(
                            line,
                            account=line.tax_line_id.cash_basis_transition_account_id,
                        )
                    elif line.tax_ids:
                        # Base line.
                        grouping_key = self.env['account.partial.reconcile']._get_cash_basis_base_line_grouping_key_from_record(
                            line,
                            account=line.company_id.account_cash_basis_base_account_id,
                        )

                    if grouping_key not in account_vals_to_fix:
                        continue

                    account_vals_to_fix[grouping_key]['debit'] -= line.debit
                    account_vals_to_fix[grouping_key]['credit'] -= line.credit

                # ==========================================================================
                # Generate the exchange difference journal items:
                # - to reset the balance of all transfer account to zero.
                # - fix rounding issues on the tax account/base tax account.
                # ==========================================================================

                for values in account_vals_to_fix.values():
                    balance = values['debit'] - values['credit']

                    if move.company_currency_id.is_zero(balance):
                        continue

                    if values.get('tax_repartition_line_id'):
                        # Tax line.
                        tax_repartition_line = self.env['account.tax.repartition.line'].browse(values['tax_repartition_line_id'])
                        account = tax_repartition_line.account_id or self.env['account.account'].browse(values['account_id'])

                        sequence = len(exchange_diff_move_vals['line_ids'])
                        exchange_diff_move_vals['line_ids'] += [
                            (0, 0, {
                                **values,
                                'name': _('Currency exchange rate difference (cash basis)'),
                                'debit': balance if balance > 0.0 else 0.0,
                                'credit': -balance if balance < 0.0 else 0.0,
                                'account_id': account.id,
                                'sequence': sequence,
                            }),
                            (0, 0, {
                                **values,
                                'name': _('Currency exchange rate difference (cash basis)'),
                                'debit': -balance if balance < 0.0 else 0.0,
                                'credit': balance if balance > 0.0 else 0.0,
                                'account_id': values['account_id'],
                                'tax_ids': [],
                                'tax_tag_ids': [],
                                'tax_repartition_line_id': False,
                                'sequence': sequence + 1,
                            }),
                        ]
                    else:
                        # Base line.
                        sequence = len(exchange_diff_move_vals['line_ids'])
                        exchange_diff_move_vals['line_ids'] += [
                            (0, 0, {
                                **values,
                                'name': _('Currency exchange rate difference (cash basis)'),
                                'debit': balance if balance > 0.0 else 0.0,
                                'credit': -balance if balance < 0.0 else 0.0,
                                'sequence': sequence,
                            }),
                            (0, 0, {
                                **values,
                                'name': _('Currency exchange rate difference (cash basis)'),
                                'debit': -balance if balance < 0.0 else 0.0,
                                'credit': balance if balance > 0.0 else 0.0,
                                'tax_ids': [],
                                'tax_tag_ids': [],
                                'sequence': sequence + 1,
                            }),
                        ]

        if not self:
            return self.env['account.move']

        company = self[0].company_id
        journal = company.currency_exchange_journal_id

        exchange_diff_move_vals = {
            'move_type': 'entry',
            'date': date.min,
            'journal_id': journal.id,
            'line_ids': [],
            'currency_id':self.env.company.currency_id.parent_id.id,
            'asiento_diferencial':True,
        }

        # Fix residual amounts.
        to_reconcile = _add_lines_to_exchange_difference_vals(self, exchange_diff_move_vals)

        # Fix cash basis entries.
        is_cash_basis_needed = self[0].account_internal_type in ('receivable', 'payable')
        if is_cash_basis_needed:
            _add_cash_basis_lines_to_exchange_difference_vals(self, exchange_diff_move_vals)

        # ==========================================================================
        # Create move and reconcile.
        # ==========================================================================

        if exchange_diff_move_vals['line_ids']:
            # Check the configuration of the exchange difference journal.
            if not journal:
                raise UserError(_("You should configure the 'Exchange Gain or Loss Journal' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            if not journal.company_id.expense_currency_exchange_account_id:
                raise UserError(_("You should configure the 'Loss Exchange Rate Account' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            if not journal.company_id.income_currency_exchange_account_id.id:
                raise UserError(_("You should configure the 'Gain Exchange Rate Account' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))

            exchange_diff_move_vals['date'] = max(exchange_diff_move_vals['date'], company._get_user_fiscal_lock_date())

            exchange_move = self.env['account.move'].create(exchange_diff_move_vals)
        else:
            return None

        # Reconcile lines to the newly created exchange difference journal entry by creating more partials.
        partials_vals_list = []
        for source_line, sequence in to_reconcile:
            exchange_diff_line = exchange_move.line_ids[sequence]

            if source_line.company_currency_id.is_zero(source_line.amount_residual):
                exchange_field = 'amount_residual_currency'
            else:
                exchange_field = 'amount_residual'

            if exchange_diff_line[exchange_field] > 0.0:
                debit_line = exchange_diff_line
                credit_line = source_line
            else:
                debit_line = source_line
                credit_line = exchange_diff_line

            partials_vals_list.append({
                'amount': abs(source_line.amount_residual),
                'debit_amount_currency': abs(debit_line.amount_residual_currency),
                'credit_amount_currency': abs(credit_line.amount_residual_currency),
                'debit_move_id': debit_line.id,
                'credit_move_id': credit_line.id,
            })

        self.env['account.partial.reconcile'].create(partials_vals_list)

        return exchange_move