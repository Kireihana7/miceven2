# -*- coding: utf-8 -*-

from odoo import models, fields,api

class HRPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.depends('amount')
    def _amount_usd(self):
        tax_today_id = self.env['res.currency'].search([('name', '=', 'USD')])

        for record in self:
            record[("amount_usd")] = record.amount * tax_today_id.rate


    amount_usd = fields.Float(store=True, readonly=True, compute="_amount_usd", string="Importe (USD)", default=0)
    is_incidence=fields.Boolean(string="Incidencia")
