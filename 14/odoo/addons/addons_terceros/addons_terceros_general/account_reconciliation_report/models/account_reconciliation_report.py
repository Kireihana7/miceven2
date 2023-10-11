# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError



class AccountReconciliationReport(models.TransientModel):
    _name = 'account.reconciliation.report'
    _description = "Account Reconciliation Report"

    journal_ids = fields.Many2many('account.journal', string='Journals',
                               required=True,
                               domain="[('type','in',('cash','bank','general'))]",
                               default=lambda self: self.env[
                                   'account.journal'].search([('type', 'in', ('cash','bank','general'))]))
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    def print_report(self):
        codes = []
        account_ids = []
        default_ids = []
        debit_ids   = []
        credit_ids  = []
        datas = []
        debit_total = 0
        credit_total = 0
        balance_debit = 0
        balance_credit = 0
        amount_currency_debit = 0
        amount_currency_credit = 0
        if self.journal_ids:
            codes = [journal.id for journal in self.journal_ids]
            default_ids = [journal.default_account_id.id for journal in self.journal_ids]
            debit_ids = [journal.payment_debit_account_id.id for journal in self.journal_ids]
            credit_ids = [journal.payment_credit_account_id.id for journal in self.journal_ids]
        #account_ids = default_ids + debit_ids + credit_ids
        domain = [
        ('move_id.state', '=', 'posted'), 
        ('company_id', '=', self.company_id.id),
        ('journal_id', 'in', codes),
        '|',
        '|',
        ('account_id', 'in', default_ids),
        ('account_id', 'in', debit_ids),
        ('account_id', 'in', credit_ids),
        ]
        invoice = self.env["account.move.line"].search(domain,order='date asc')
        if not invoice:
            raise UserError('¡Felicitaciones! No hay nada por Conciliar.')
        for invoices in invoice:
            amount_currency_debit = 0
            balance_debit = 0
            amount_currency_credit = 0
            balance_credit = 0

            if invoices['account_id'] == invoices.journal_id.payment_debit_account_id.id:
                debit_total += residual_amount
                amount_currency_debit = invoices['amount_residual_currency'] if invoices['reconcile'] else invoices['amount_currency']
                balance_debit = invoices['amount_residual'] if invoices['reconcile'] else invoices['balance']

            if invoices['account_id'] == invoices.journal_id.payment_credit_account_id.id:
                credit_total += residual_amount
                amount_currency_credit = invoices['amount_residual_currency'] if invoices['reconcile'] else invoices['amount_currency']
                balance_credit = invoices['amount_residual'] if invoices['reconcile'] else invoices['balance']
            datas.append({
                'partner_name':     invoices.partner_id.name,
                'date':             invoices.date,
                'journal_name':     invoices.journal_id.name,
                'amount_currency_debit': amount_currency_debit,
                'balance_debit': balance_debit,
                'amount_currency_credit': amount_currency_credit,
                'balance_credit': balance_credit,
                })

        res = {
            'company_name':         self.company_id.name,
            'company_vat':          self.company_id.vat[:10] if self.company_id.vat else ''+'-'+self.company_id.vat[10:] if self.company_id.vat else '',
            'invoices':             datas,
            'debit_total':          debit_total,
            'credit_total':         credit_total,
        }
        data = {
            'form': res,
        }
        return self.env.ref('account_reconciliation_report.account_reconciliation_report').report_action([],data=data)