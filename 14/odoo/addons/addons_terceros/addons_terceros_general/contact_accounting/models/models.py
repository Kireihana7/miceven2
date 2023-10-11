# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class AccountPayment(models.Model):
    _inherit = 'res.partner'

    def show_accounting_plan(self):
        self.ensure_one()
        res = self.env.ref('contact_accounting.action_view_account_partner_activity')
        res = res.read()[0]
        res['domain'] = str([('partner_id', '=', self.id)])
        return res

