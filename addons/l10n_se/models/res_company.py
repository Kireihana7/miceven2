# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import re


class ResCompany(models.Model):
    _inherit = 'res.company'

    org_number = fields.Char(compute='_compute_org_number')

    @api.depends('vat')
    def _compute_org_number(self):
        for company in self:
<<<<<<< HEAD
            if company.account_fiscal_country_id.code == "SE" and company.vat:
=======
            if company.country_id.code == "SE" and company.vat:
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                org_number = re.sub(r'\D', '', company.vat)[:-2]
                org_number = org_number[:6] + '-' + org_number[6:]

                company.org_number = org_number
            else:
                company.org_number = ''
