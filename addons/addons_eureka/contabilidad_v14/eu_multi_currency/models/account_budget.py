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

from odoo import api, fields, models, _
from math import copysign

class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    tasa_presu = fields.Float(string="Tasa del Presupuesto",compute="_compute_tasa_presu",store=True)

    @api.depends('company_id')
    def _compute_tasa_presu(self):
      for record in self:
        record.tasa_presu = record.env.company.currency_id.parent_id._convert(1, record.env.company.currency_id, record.company_id or self.env.company, fields.date.today())

class CrossoveredBudgetLine(models.Model):
    _inherit = 'crossovered.budget.lines'
    restante_amount = fields.Float(string="Importe Restante",compute="_compute_restante_amount")

    @api.depends('planned_amount','practical_amount')
    def _compute_restante_amount(self):
        for rec in self:
            rec.restante_amount = 0.0
            if rec.planned_amount and rec.practical_amount:
                rec.restante_amount = rec.planned_amount - rec.practical_amount
    currency_id_dif = fields.Many2one(related="currency_id.parent_id",
        string="Divisa de Referencia",)
    practical_amount_usd = fields.Monetary(
        compute='_compute_practical_amount_usd', string='Importe Real $')
    planned_amount_usd = fields.Monetary(
        'Importe Previsto $', compute='_compute_planned_amount_usd',store=True,readonly=True)

    def _compute_practical_amount_usd(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount_usd) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('move_id.state', '=', 'posted')
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit_usd)-sum(debit_usd) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.practical_amount_usd = self.env.cr.fetchone()[0] or 0.0

    @api.depends('planned_amount','currency_id_dif','currency_id','company_id')
    def _compute_planned_amount_usd(self):
      for record in self:
        record.planned_amount_usd = record.env.company.currency_id._convert(record['planned_amount'], record.env.company.currency_id.parent_id, record.company_id or self.env.company, fields.date.today())