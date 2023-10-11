<<<<<<< HEAD
# -*- coding: utf-8 -*-
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountChartTemplate(models.Model):
<<<<<<< HEAD
    _inherit = 'account.chart.template'

    def _load(self, company):
        """
            Override normal default taxes, which are the ones with lowest sequence.
        """
        result = super()._load(company)
        template = company.chart_template_id
        if template == self.env.ref('l10n_it.l10n_it_chart_template_generic'):
            company.account_sale_tax_id = self.env.ref(f'l10n_it.{company.id}_22v')
            company.account_purchase_tax_id = self.env.ref(f'l10n_it.{company.id}_22am')
=======

    _inherit = 'account.chart.template'

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        res = super()._load(sale_tax_rate, purchase_tax_rate, company)
        if self == self.env.ref('l10n_it.l10n_it_chart_template_generic', raise_if_not_found=False):
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            tax = self.env.ref(f'l10n_it.{company.id}_00eu', raise_if_not_found=False)
            if tax:
                tax.write({
                    'l10n_it_has_exoneration': True,
                    'l10n_it_kind_exoneration': 'N3.2',
                    'l10n_it_law_reference': 'Art. 41, DL n. 331/93',
                })
<<<<<<< HEAD
        return result
=======
        return res
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
