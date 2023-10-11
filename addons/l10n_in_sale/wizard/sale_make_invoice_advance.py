# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, so_line):
        res = super()._prepare_invoice_values(order, so_line)
        if order.l10n_in_journal_id:
            res['journal_id'] = order.l10n_in_journal_id.id
<<<<<<< HEAD
        if order.country_code == 'IN':
=======
        if order.l10n_in_company_country_code == 'IN':
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            res['l10n_in_gst_treatment'] = order.l10n_in_gst_treatment
        if order.l10n_in_reseller_partner_id:
            res['l10n_in_reseller_partner_id'] = order.l10n_in_reseller_partner_id
        return res
