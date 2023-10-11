# -*- coding: utf-8 -*-
# Jose Mazzei - 6
from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo.exceptions import UserError

class EuReportePaymentDate(models.TransientModel):
    _name = 'eu.reporte.payment.date'
    _description = "Reporte Cobros en Bancos"

    start_date = fields.Date('Fecha Desde', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    end_date = fields.Date("Fecha Hasta", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    partner_ids = fields.Many2many('res.partner', string='Cliente')
    # UPDATE: Vendedores
    user_ids = fields.Many2many("res.users", string="Vendedores")    
    journal_id = fields.Many2many('account.journal', string='Diario',domain="[('type', 'in', ('bank','cash'))]")
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )


    def action_generate_report(self):
        # domain = [
        # ('company_id', '=', self.company_id.id),
        # ('date', '>=', self.start_date),
        # ('date', '<=', self.end_date),
        # ('state','=','posted'),
        # ('payment_type','=','inbound'),
        # ('partner_type','=','customer'),
        # ]
        domain = [
            ('company_id', '=', self.company_id.id),
            ('payment_date_collection', '>=', self.start_date),
            ('payment_date_collection', '<=', self.end_date),
            ('state', '=', 'posted'),
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
        ]
        if self.journal_id:
            domain.append(('journal_id', 'in', self.journal_id.ids))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        #if self.currency_id:
        #    domain.append(('currency_id', '=', self.currency_id.id))
        # UPDATE: Vendedores
        if self.user_ids:
            domain.append(('sale_id.user_id', 'in', self.user_ids.ids))

        datas = []
        fechas = []
        journals = []
        payment = self.env["account.payment"].search(domain,order='payment_date_collection asc')
        fechas.append({
            
            })
        total_amount = 0
        total_amount_ref = 0
        efectivo_usd = sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id != x.company_id.currency_id).mapped('amount_ref'))
        efectivo_bs  = sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id != x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id == x.company_id.currency_id).mapped('amount_ref'))
        banco_usd    = sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id != x.company_id.currency_id).mapped('amount_ref'))
        banco_bs     = sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id != x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id == x.company_id.currency_id).mapped('amount_ref'))
        if not payment:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        pago_existe = False
        for invoices in payment.sorted(lambda r: (r.journal_id)):
            total_amount += round(invoices.amount,2) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,2)
            total_amount_ref += round(invoices.amount,2) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,2)
            datas.append({
                'date':    str(invoices.payment_date_collection.strftime("%d/%m/%Y")),
                'partner_id': invoices.partner_id.name,
                'payment_id': invoices.name,
                'ref':    invoices.ref,
                'description': invoices.ref_bank,
                'rate': round(invoices.manual_currency_exchange_rate,4),
                'amount': round(invoices.amount,2) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,2),
                'currency_id': invoices.currency_id.name,
                'amount_ref': round(invoices.amount,2) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,2),
                })
        moneda_diario = False
        for journal in payment.mapped('journal_id').sorted(lambda x: x.currency_id):
            moneda_diario = journal.currency_id if journal.currency_id else self.env.company.currency_id
            journals.append({
                'journal_id': journal.name,
                'journal_currency': moneda_diario.symbol,
                'monto_moneda_diario': 0 + sum(payment.filtered(lambda x: x.journal_id.id == journal.id and x.currency_id == moneda_diario).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.id == journal.id and x.currency_id != moneda_diario).mapped('amount_ref')),
            })
        res = {
            'start_date':   str(self.start_date.strftime("%d/%m/%Y")),
            'end_date':     str(self.end_date.strftime("%d/%m/%Y")),
            'company_name': self.company_id.name,
            'journal_id': False,
            'company_vat':  self.company_id.vat,
            'invoices':     datas,
            'total_amount':round(total_amount,2),
            'total_amount_ref':round(total_amount_ref,2),
            'efectivo_usd':round(efectivo_usd,2),
            'efectivo_bs':round(efectivo_bs,2),
            'banco_usd':round(banco_usd,2),
            'banco_bs':round(banco_bs,2),
            'journals':journals,
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_account_reports.action_report_eu_reporte_payment_date').report_action([],data=data)