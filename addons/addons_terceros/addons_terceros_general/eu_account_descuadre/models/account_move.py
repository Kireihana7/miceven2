# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    debit_total = fields.Float(compute='_compute_descuadrado', string="Total Débito",store=True)
    credit_total = fields.Float(compute='_compute_descuadrado',string="Total Crédito",store=True)
    descuadrado = fields.Boolean(compute="_compute_descuadrado",string="Descuadrado",store=True)


    def action_post(self):
        for rec in self:
            if rec.descuadrado and rec.move_type == 'entry':
                raise UserError('No puedes publicar un asiento descuadrado')
        return super(AccountMove, self).action_post()

    @api.depends('line_ids')
    def _compute_descuadrado(self):
        for invoice in self:
            debit = 0
            credit = 0
            debit = round(sum(invoice.line_ids.mapped('debit')),2)
            credit = round(sum(invoice.line_ids.mapped('credit')),2)
            #for lines in invoice.line_ids:
            #    debit += lines.debit 
            #    credit += lines.credit
            invoice.debit_total = debit
            invoice.credit_total = credit
            total = debit - credit
            invoice.descuadrado = True if debit != credit and invoice.move_type == 'entry' else False

    def _check_balanced(self):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return
        debit = 0 
        credit = 0 
        for line in moves.line_ids:
            debit  = debit  + round(line.debit,moves[0].company_currency_id.decimal_places)  
            credit = credit + round(line.credit,moves[0].company_currency_id.decimal_places)

        self.env['account.move.line'].flush(self.env['account.move.line']._fields)
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
            SELECT line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places)
            FROM account_move_line line
            JOIN account_move move ON move.id = line.move_id
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_company company ON company.id = journal.company_id
            JOIN res_currency currency ON currency.id = company.currency_id
            WHERE line.move_id IN %s
            GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
        ''', [tuple(self.ids)])

        query_res = self._cr.fetchall()
        sums = 0 
        if query_res:
            sums = query_res[0][1]

        diff = self.env['account.move.line']
        if int(sums) > 1:
            return super(AccountMove, self)._check_balanced()
        
        if sums != 0:
            if debit > credit:
                diff = self.env['account.move.line'].search([('move_id','=',self.id), ('credit','>','0')],limit=1)
                amount = round(diff.credit,moves[0].company_currency_id.decimal_places) + sums
                sql = "UPDATE account_move_line SET credit = " + str(amount ) + " WHERE id = " + str(diff.id)
                self._cr.execute(sql)

            else :
                diff = self.env['account.move.line'].search([('move_id','=',self.id), ('debit','>','0')],limit=1)
                amount = round(diff.debit,moves[0].company_currency_id.decimal_places) + sums
                sql = "UPDATE account_move_line SET debit = " + str(amount ) + " WHERE id = " + str(diff.id)
                self._cr.execute(sql)
        return super(AccountMove, self)._check_balanced()
        
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    descuadrado = fields.Boolean(related='move_id.descuadrado',store=True)