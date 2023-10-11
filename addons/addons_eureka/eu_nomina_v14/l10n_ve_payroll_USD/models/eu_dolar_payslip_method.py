# -*- coding: utf-8 -*-

from datetime import datetime, timedelta,date
from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


TODAY=datetime.today()
class HRPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'
    
    @api.depends('amount','slip_id.tax_today')
    def _amount_usd(self):
        tax_today_id = round(self.company_id.currency_id.parent_id.rate,4) #si se cambia la compañia a dolares esto deberia cambiar
        for record in self:
            record[("amount_usd")] = round(record.amount,4) * (round(record.slip_id.tax_today,4) if record.slip_id.tax_today<=1 else 1/record.slip_id.tax_today)

    @api.depends('total','slip_id.tax_today')
    def _total_usd(self):
        tax_today= round(self.company_id.currency_id.parent_id.rate,4) #si se cambia la compañia a dolares esto deberia cambiar
        for record in self:
            record[("total_usd")] = round(round(record.total,4) * (round(record.slip_id.tax_today,4) if record.slip_id.tax_today<=1 else 1/round(record.slip_id.tax_today,2)),2)
class HRContract(models.Model):
    _inherit = 'hr.contract'
    currency_id_dif = fields.Many2one("res.currency", 
        string="Referencia en Divisa",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'VEF')], limit=1),)
    @api.depends('currency_id_dif','currency_id')
    def _tax_today(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
                record[("tax_today")] = record.currency_id_dif.rate
    @api.depends('wage','currency_id_dif','tax_today','complemento','cesta_ticket')
    def _amount_all_usd(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
            record[("amount_total_usd")]    = (+record.wage+record.cesta_ticket) / record.tax_today + record.complemento
class EuCollectiveContract(models.Model):
    _inherit="hr.payslip"
    
    currency_id_dif = fields.Many2one("res.currency", 
        string="Referencia en Divisa",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'VEF')], limit=1),)
    tax_today= fields.Float(readonly=False, compute="_tax_today", default= lambda self: self.env['res.currency'].search([('name', '=', 'VEF')]).rate,store=True, string="Tasa del Día") 

    def _action_create_account_move(self):

        precision = self.env['decimal.precision'].precision_get('Payroll')
        currency=self.env['res.currency'].search([('name', '=', 'VEF')], limit=1).id
        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError('One of the contract for these payslips has no structure type.')
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError('One of the payroll structures has no account journal defined on it.')

          # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slipmapped_data={}
        for journal in payslips_to_post.mapped('struct_id.journal_id.id'):

            slipmapped_data[journal] = payslips_to_post.filtered(lambda x: x.struct_id.journal_id.id==journal)
        for journal_id in slipmapped_data.keys(): # For each journal_id.
            for rate in list(set(slipmapped_data[journal_id].mapped('tax_today'))):
                per_rate_date=list(set(slipmapped_data[journal_id].filtered(lambda x: x.tax_today==rate).mapped('date_to')))
                for date in per_rate_date:
                    # for slip_date in slipmapped_data[journal_id].filtered(lambda x: x.tax_today==rate and x.date_to==date): # For each month.
                        line_ids = []
                        debit_sum = 0.0
                        credit_sum = 0.0
                        date = date
                        move_dict = {
                            'narration': '',
                            'ref': date.strftime('%d %B %Y'),
                            'journal_id': journal_id,
                            'date': date,
                            'currency_id':currency,
                            'manual_currency_exchange_rate':round(rate,2)
                        } #aqui hubo cambio

                        for slip in slipmapped_data[journal_id].filtered(lambda x: x.tax_today==rate and x.date_to==date):
                            move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                            move_dict['narration'] += '\n'
                            slip_lines = slip._prepare_slip_lines(date, line_ids,round(rate,2))

                            line_ids.extend(slip_lines)

                        for line_id in line_ids: # Get the debit and credit sum.
                            debit_sum += line_id['debit']
                            credit_sum += line_id['credit']

                        # The code below is called if there is an error in the balance between credit and debit sum.
                        if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                            slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, date)
                        elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                            slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, date)

                        # Add accounting lines in the move
                        move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                        move = self._create_account_move(move_dict)
                        for slip in slipmapped_data[journal_id].filtered(lambda x: x.tax_today==rate and x.date_to==date):
                            slip.write({'move_id': move.id, 'date': date})
        return True


    def _prepare_slip_lines(self, date, line_ids,manual_exchange_rate):
        self.ensure_one()
        # rate=self.company_id.currency_id.rate if self.company_id.currency_id.rate>0 else 1
        currency=self.company_id.currency_id.parent_id 
        precision = self.env['decimal.precision'].precision_get('Payroll')
        new_lines = []
        for line in self.line_ids.filtered(lambda line: line.category_id):
            amount = -round(line.total_usd,2) if self.credit_note else round(line.total_usd,4)
            if line.code == 'NET': # Check if the line is the 'Net Salary'.
                for tmp_line in self.line_ids.filtered(lambda line: line.category_id):
                    if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                        if amount > 0:
                            amount -= abs(round(tmp_line.total_usd,4))
                        elif amount < 0:
                            amount += abs(round(tmp_line.total_usd,4))
            if float_is_zero(amount, precision_digits=precision):
                continue
            debit_account_id = line.salary_rule_id.account_debit.id
            credit_account_id = line.salary_rule_id.account_credit.id

            if debit_account_id: # If the rule has a debit account.
                debit = amount if amount > 0.0 else 0.0
                credit = -amount if amount < 0.0 else 0.0

                debit_line = self._get_existing_lines(
                    line_ids + new_lines, line, debit_account_id, debit, credit)

                if not debit_line:
                    debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                    debit_line['currency_id']=currency.id
                    debit_line['amount_currency']=line.total
                    debit_line['manual_currency_exchange_rate']=manual_exchange_rate
                    new_lines.append(debit_line)
                else:
                    debit_line['debit'] += debit
                    debit_line['credit'] += credit
                    debit_line['amount_currency']+=line.total

            if credit_account_id: # If the rule has a credit account.
                debit = -amount if amount < 0.0 else 0.0
                credit = amount if amount > 0.0 else 0.0
                credit_line = self._get_existing_lines(
                    line_ids + new_lines, line, credit_account_id, debit, credit)

                if not credit_line:
                    credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                    credit_line['currency_id']=currency.id
                    credit_line['amount_currency']=line.total*-1
                    credit_line['manual_currency_exchange_rate']=manual_exchange_rate
                    new_lines.append(credit_line)
                else:
                    credit_line['debit'] += debit
                    credit_line['credit'] += credit
                    credit_line['amount_currency']+=line.total*-1

        return new_lines


class HRPayslipRun(models.Model):
    _inherit="hr.payslip.run"

    currency_id_dif = fields.Many2one("res.currency", 
        string="Referencia en Divisa",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'VEF')], limit=1),)
    tax_today= fields.Float(readonly=False, compute="_tax_today", default= lambda self: self.env['res.currency'].search([('name', '=', 'VEF')]).rate,store=True, string="Tasa del Día") 