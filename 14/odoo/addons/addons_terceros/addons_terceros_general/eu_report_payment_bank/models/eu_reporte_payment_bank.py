# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo.exceptions import UserError

class EuReportePaymentBank(models.TransientModel):
    _name = 'eu.reporte.payment.bank'
    _description = "Reporte Cobros en Bancos"

    start_date = fields.Date('Desde', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    end_date = fields.Date("Hasta", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente')
    currency_id = fields.Many2one('res.currency', string='Moneda')
    journal_id = fields.Many2one('account.journal', string='Diario',domain="[('type', 'in', ('bank','cash'))]")
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )

    def action_generate_report(self):
        domain = [
        ('company_id', '=', self.company_id.id),
        ('date', '>=', self.start_date),
        ('date', '<=', self.end_date),
        ]
        if self.journal_id:
            domain.append(('journal_id', '=', self.journal_id.id))
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        if self.currency_id:
            domain.append(('currency_id', '=', self.currency_id.id))

        datas = []
        fechas = []
        payment = self.env["account.payment"].search(domain,order='date asc')
        fechas.append({
            
            })
        total_amount = 0
        total_amount_ref = 0
        if not payment:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        for invoices in payment:
            total_amount += round(invoices.amount,2) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,2)
            total_amount_ref += round(invoices.amount,2) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,2)
            datas.append({
                'date':    invoices.date,
                'payment_id': invoices.name,
                'partner_id': invoices.partner_id.name,
                'journal_id': invoices.journal_id.name,
                'ref':    invoices.ref,
                'amount': round(invoices.amount,2) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,2),
                'currency_id': invoices.currency_id.name,
                'amount_ref': round(invoices.amount,2) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,2),
                'currency_id_ref': invoices.currency_id_ref.name,
                })
        res = {
            'start_date':   self.start_date,
            'end_date':     self.end_date,
            'company_name': self.company_id.name,
            'journal_id': self.journal_id.name,
            'company_vat':  self.company_id.vat,
            'invoices':     datas,
            'total_amount':round(total_amount,2),
            'total_amount_ref':round(total_amount_ref,2),
            'enero':round(sum(payment.filtered(lambda x: int(x.date.month) == 1 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 1 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'febrero':round(sum(payment.filtered(lambda x: int(x.date.month) == 2 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 2 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'marzo':round(sum(payment.filtered(lambda x: int(x.date.month) == 3 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 3 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'abril':round(sum(payment.filtered(lambda x: int(x.date.month) == 4 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 4 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'mayo':round(sum(payment.filtered(lambda x: int(x.date.month) == 5 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 5 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'junio':round(sum(payment.filtered(lambda x: int(x.date.month) == 6 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 6 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'julio':round(sum(payment.filtered(lambda x: int(x.date.month) == 7 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 7 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'agosto':round(sum(payment.filtered(lambda x: int(x.date.month) == 8 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 8 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'septiembre':round(sum(payment.filtered(lambda x: int(x.date.month) == 9 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 9 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'octubre':round(sum(payment.filtered(lambda x: int(x.date.month) == 10 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 10 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'noviembre':round(sum(payment.filtered(lambda x: int(x.date.month) == 11 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 11 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
            'diciembre':round(sum(payment.filtered(lambda x: int(x.date.month) == 12 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: int(x.date.month) == 12 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),2),
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_report_payment_bank.action_report_eu_reporte_payment_bank').report_action([],data=data)