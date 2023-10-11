# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    @api.model
    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(
            acc_template_ref, company, journals_dict)
        if company.account_fiscal_country_id.code != 'FR':
            return journal_data

        for journal in journal_data:
<<<<<<< HEAD
            if journal['type'] in ('sale', 'purchase'):
=======
            if journal['type'] in ('sale', 'purchase') and company.country_id.code == "FR":
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                journal.update({'refund_sequence': True})
        return journal_data
