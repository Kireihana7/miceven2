# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
import re
from math import copysign
import itertools
from collections import defaultdict
from dateutil.relativedelta import relativedelta


class AccountReconcileModel(models.Model):
    _inherit = 'account.reconcile.model'

    
    match_text_location_reference_estrict = fields.Boolean(
        default=False,
        help="Buscar de manera estricta por Referencia",
    )
      
    def _get_invoice_matching_query(self, st_lines_with_partner, excluded_ids):
        self.ensure_one()
        if not self.match_text_location_reference_estrict:
            return super(AccountReconcileModel, self)._get_invoice_matching_query(st_lines_with_partner, excluded_ids)
        else:
            if self.rule_type != 'invoice_matching':
                raise UserError(_('Programmation Error: Can\'t call _get_invoice_matching_query() for different rules than \'invoice_matching\''))
            unaccent = get_unaccent_wrapper(self._cr)
            query = r'''
            SELECT
                st_line.id                          AS id,
                aml.id                              AS aml_id,
                aml.currency_id                     AS aml_currency_id,
                aml.date_maturity                   AS aml_date_maturity,
                aml.amount_residual                 AS aml_amount_residual,
                aml.amount_residual_currency        AS aml_amount_residual_currency,
                ''' + self._get_select_communication_flag() + r''' AS communication_flag,
                ''' + self._get_select_payment_reference_flag() + r''' AS payment_reference_flag
            FROM account_bank_statement_line st_line
            JOIN account_move st_line_move          ON st_line_move.id = st_line.move_id
            JOIN res_company company                ON company.id = st_line_move.company_id
            , account_move_line aml
            LEFT JOIN account_move move             ON move.id = aml.move_id AND move.state = 'posted'
            LEFT JOIN account_account account       ON account.id = aml.account_id
            LEFT JOIN res_partner aml_partner       ON aml.partner_id = aml_partner.id
            LEFT JOIN account_payment payment       ON payment.move_id = move.id
            WHERE
                aml.company_id = st_line_move.company_id
                AND aml.journal_id = st_line_move.journal_id
                AND move.state = 'posted'
                AND account.reconcile IS TRUE
                AND aml.reconciled IS FALSE
            '''

            # Add conditions to handle each of the statement lines we want to match
            st_lines_queries = []
            for st_line, partner in st_lines_with_partner:
                # In case we don't have any partner for this line, we try assigning one with the rule mapping
                if st_line.amount > 0:
                    st_line_subquery = r"aml.balance > 0"
                else:
                    st_line_subquery = r"aml.balance < 0"
                if self.match_text_location_reference_estrict:
                    st_line_subquery += r" AND move.ref = aml.ref AND st_line_move.ref = move.ref"

                st_lines_queries.append(r"st_line.id = %s AND (%s)" % (st_line.id, st_line_subquery))

            query += r" AND (%s) " % " OR ".join(st_lines_queries)

            params = {}

            # If this reconciliation model defines a past_months_limit, we add a condition
            # to the query to only search on move lines that are younger than this limit.
            if self.past_months_limit:
                date_limit = fields.Date.context_today(self) - relativedelta(months=self.past_months_limit)
                query += "AND aml.date >= %(aml_date_limit)s"
                params['aml_date_limit'] = date_limit

            # Filter out excluded account.move.line.
            if excluded_ids:
                query += 'AND aml.id NOT IN %(excluded_aml_ids)s'
                params['excluded_aml_ids'] = tuple(excluded_ids)

            if self.matching_order == 'new_first':
                query += ' ORDER BY aml_date_maturity DESC, aml_id DESC'
            else:
                query += ' ORDER BY aml_date_maturity ASC, aml_id ASC'
            #raise UserError(query)
            return query, params