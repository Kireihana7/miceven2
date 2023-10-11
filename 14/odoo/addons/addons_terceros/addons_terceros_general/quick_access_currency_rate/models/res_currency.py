# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def service_get_currencies(self):
        res = self.search_read(
            fields=['name', 'symbol', 'date', 'rate'], order='date')
        return res

    @api.model
    def service_set_currency_rates(self, vals):
        if not vals:
            return
        CurrencyRate = self.env['res.currency.rate']
        for currency_id, rate in vals.items():
            currency_id = int(currency_id)
            new_vals = {'currency_id': currency_id, 'rate': rate}
            dm = [('currency_id', '=', currency_id),
                  ('name', '=', fields.Date.today().strftime(DF))]
            exist = CurrencyRate.search(dm, limit=1)
            if exist:
                exist.write(new_vals)
            else:
                CurrencyRate.create(new_vals)
