# -*- coding: utf-8 -*-

from odoo import models, fields,api

class HRPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    @api.depends('amount')
    def _amount_usd(self):
        tax_today_id = self.company_id.currency_id.rate #si se cambia la compañia a dolares esto deberia cambiar
        for record in self:
            record[("amount_usd")] = record.amount * (tax_today_id if tax_today_id<=1 else 1/tax_today_id)

    @api.depends('total')
    def _total_usd(self):
        tax_today_id = self.company_id.currency_id.rate #si se cambia la compañia a dolares esto deberia cambiar
        for record in self:
            record[("total_usd")] = record.total * (tax_today_id if tax_today_id<=1 else 1/tax_today_id)



    amount_usd = fields.Float(store=True, readonly=True, compute="_amount_usd", string="Importe REF.", default=0)
    total_usd = fields.Float(store=True, readonly=True, compute="_total_usd", string="Total REF.", default=0)


