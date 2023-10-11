# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models,_
from odoo.exceptions import UserError


class GenerateOpeningEntries(models.TransientModel):
    _name = 'generate.opening.entries'
    _description = "Generate Opening Entries"

    name = fields.Char("Name of new entries", required=True,
                       default='End of Fiscal Year Entry')
    old_fiscal_year_id = fields.Many2one(
        'sh.fiscal.year', string="Fiscal Year to close", required=True)
    new_fiscal_year_id = fields.Many2one(
        'sh.fiscal.year', string="New Fiscal Year", required=True)
    journal_id = fields.Many2one('account.journal', string="Opening Entries Journal",
                                 required=True, domain=[('type', '=', 'opening')])
    period_id = fields.Many2one(
        'sh.account.period', string="Opening Entries Period", required=True)

    def data_save(self):
        """
        This function close account fiscalyear and create entries in new fiscalyear
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscalyear close state’s IDs

        """
        obj_acc_move = self.env['account.move']
        obj_acc_move_line = self.env['account.move.line']
        total_debit = 0.0
        total_credit = 0.0

        self._cr.execute("SELECT id FROM sh_account_period WHERE date_end < (SELECT date_start FROM sh_fiscal_year WHERE id = %s)", (str(
            self.new_fiscal_year_id.id),))
        fy_period_set = ','.join(
            map(lambda id: str(id[0]), self._cr.fetchall()))
        self._cr.execute("SELECT id FROM sh_account_period WHERE date_start > (SELECT date_end FROM sh_fiscal_year WHERE id = %s)", (str(
            self.old_fiscal_year_id.id),))
        fy2_period_set = ','.join(
            map(lambda id: str(id[0]), self._cr.fetchall()))

        if not fy_period_set or not fy2_period_set:
            raise UserError(_(
                'The periods to generate opening entries cannot be found.'))

        period = self.period_id
        new_fyear = self.new_fiscal_year_id
        old_fyear = self.old_fiscal_year_id

        new_journal = self.journal_id
        company_id = self.journal_id.company_id.id

        if not new_journal.payment_credit_account_id or not new_journal.payment_debit_account_id:
            raise UserError(_(
                'The journal must have default credit and debit account.'))

        #delete existing move and move lines if any
        move_ids = obj_acc_move.search(
            [('journal_id', '=', new_journal.id), ('period_id', '=', period.id)])

        if move_ids:
            move_line_ids = obj_acc_move_line.search(
                [('move_id', 'in', move_ids.ids)])
            move_line_ids.unlink()
            move_ids.unlink()

        self._cr.execute(
            "SELECT id FROM sh_fiscal_year WHERE date_end < %s", (str(new_fyear.date_start),))
        result = self._cr.dictfetchall()
        fy_ids = [x['id'] for x in result]
        query_line = '''account_move_line.parent_state = 'posted' AND account_move_line.period_id IN (SELECT id FROM sh_account_period WHERE fiscal_year_id = %s)''' % (
            fy_ids[-1])

#
        #create the opening move
        rate = self.env.company.currency_id.parent_id.rate
        vals = {
            'name': '/',
            'ref': 'Opening Balance Entry',
            'move_type':'entry',
            'period_id': period.id,
            'date': period.date_start,
            'journal_id': new_journal.id,
            'currency_id': self.env.company.currency_id.id,
            'manual_currency_exchange_rate': rate,
            'apply_manual_currency_exchange':True,
        }
        move_id = obj_acc_move.create(vals)

        #1. report of the accounts with defferal method == 'unreconciled'
        self._cr.execute('''
            SELECT a.id,a.code,a.name,t.name
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type_id = t.id)
            WHERE a.deprecated = 'f' AND substring(a.code,1,1) IN ('4','5','6','7','8') AND t.id IN (13,14,15,17) AND a.company_id = %s
              AND a.reconcile = %s''', (company_id, False, ))
        account_ids = [res[0] for res in self._cr.fetchall()]
        debit = 0 
        credit = 0
        if account_ids:
            account = self.env['account.account'].search([('id','in',account_ids)])
            for acc in account:
                debit = 0 
                credit = 0
                balance = round(sum(self.env['account.move.line'].search([('account_id','=',acc.id),('fiscal_year','=',self.old_fiscal_year_id.id),('parent_state','=','posted')]).mapped('balance')),4) *-1
                if balance != 0:
                    query_1st_part = """
                    INSERT INTO account_move_line (
                         debit, credit, name, date, move_id, journal_id, period_id,
                         account_id, currency_id,company_currency_id, amount_currency, company_id,balance,debit_usd,credit_usd,balance_usd) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s)
                    """
                    query_2nd_part_args = []
                    # asiento = {
                    #     'account_id': acc.id,
                    #     'company_id': self.env.company.id,
                    #     'currency_id': self.env.company.currency_id.id,
                    #     'date': period.date_start,
                    #     'move_id': move_id.id,
                    #     'name': 'Cierre cuenta %s' % acc.code,
                    #     'journal_id': new_journal.id,
                    #     'credit': abs(balance) if balance < 0 else 0.0,
                    #     'debit': abs(balance) if balance > 0 else 0.0,
                    #     'balance': abs(balance) if balance > 0 else abs(balance) *-4,
                    #     'amount_currency': abs(balance) if balance > 0 else abs(balance) *-1,
                    # }
                    query_2nd_part_args +=(
                        balance > 0 and balance or 0.0,
                        balance < 0 and -balance or 0.0,
                        'Cierre cuenta %s' % acc.code,
                        period.date_start,
                        move_id.id,
                        new_journal.id,
                        period.id,
                        acc.id,
                        self.env.company.currency_id.id,
                        self.env.company.currency_id.id,
                        balance,
                        self.env.company.id,
                        balance,
                        balance*rate > 0 and balance*rate or 0.0,
                        balance*rate < 0 and -balance*rate or 0.0,
                        balance*rate,
                    )
                    self._cr.execute(query_1st_part,
                             tuple(query_2nd_part_args))
                    #move_line_obj = self.env['account.move.line']
                    #move_line_obj.with_context(check_move_validity=False).create(asiento)

        account_debit_new = new_journal.payment_debit_account_id
        account_credit_new = new_journal.payment_credit_account_id  

        move_lines = obj_acc_move_line.sudo().search(
            [('move_id', '=', move_id.id)])
        for line in move_lines:
            total_credit += line.credit
            total_debit += line.debit
            #line._compute_balance()

        if total_credit < 0.0:
            total_credit = - total_credit
        if total_debit < 0.0:
            total_debit = - total_debit
        # Credit Line
        asiento = {
            'account_id': account_credit_new.id,
            'company_id': self.env.company.id,
            'currency_id': self.env.company.currency_id.id,
            'date': period.date_start,
            'move_id': move_id.id,
            'name': 'Centralización de Crédito',
            'journal_id': new_journal.id,
            'debit': total_credit,
            'credit': 0,
            'balance': abs(total_credit),
            'amount_currency': abs(total_credit),
        }
        move_line_obj = self.env['account.move.line']
        move_line_obj.with_context(check_move_validity=False).create(asiento)

        # Debit Line
        asiento = {
            'account_id': account_debit_new.id,
            'company_id': self.env.company.id,
            'currency_id': self.env.company.currency_id.id,
            'date': period.date_start,
            'move_id': move_id.id,
            'name': 'Centralización de Débito',
            'journal_id': new_journal.id,
            'debit': 0,
            'credit': total_debit,
            'balance': -abs(total_debit),
            'amount_currency': -abs(total_debit),
        }
        move_line_obj = self.env['account.move.line']
        move_line_obj.with_context(check_move_validity=False).create(asiento)

        # last_move_lines = obj_acc_move_line.sudo().search(
        #     [('move_id', '=', move_id.id)], limit=2, order='id desc')
        # for line in last_move_lines:
        #     line._compute_balance()

        #move_id._compute_amount()
        #move_id.write({'amount_total_signed': total_credit+total_debit})
        old_fyear.write({'move_id': move_id.id})
        return {'type': 'ir.actions.act_window_close'}
