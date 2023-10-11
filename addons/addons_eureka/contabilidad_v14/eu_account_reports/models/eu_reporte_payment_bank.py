# -*- coding: utf-8 -*-
# Jose Mazzei - 11
from odoo import models, fields, api, _
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo.exceptions import UserError, ValidationError

class EuReportePaymentBank(models.TransientModel):
    _name = 'eu.reporte.payment.bank'
    _description = "Reporte Cobros en Bancos"

    start_date = fields.Date('Fecha Desde', default=lambda self: fields.Date.to_string(date.today().replace(day=1)), required=True)
    end_date = fields.Date("Fecha Hasta", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    type_report = fields.Selection([
        ('detail_summary', 'Detallado y Resumen'),
        ('only_summary', 'Solo resumen')
    ], string="Tipo de Reporte", required=True)
    partner_ids = fields.Many2many('res.partner', string='Cliente')
    # UPDATE: Vendedores
    user_ids = fields.Many2many("res.users", string="Vendedores")
    # journal_id = fields.Many2many('account.journal', string='Diario',domain="[('type', 'in', ('bank','cash'))]")
    journal_id = fields.Many2many('account.journal', string='Diario')
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )

    def action_generate_report(self):
        # Validación de fechas:
        if self.start_date > self.end_date:
            raise ValidationError(_('La fecha de inicio no puede ser mayor a la fecha fin.'))            
        domain = [
            ('company_id', '=', self.company_id.id),
            ('payment_reg', '>=', self.start_date),
            ('payment_reg', '<=', self.end_date),
            ('state', '=', 'posted'),
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
            ('is_internal_transfer', '=', False)
        ]
        if self.journal_id:
            domain.append(('journal_id', 'in', self.journal_id.ids))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        # UPDATE: Vendedores
        if self.user_ids:
            domain.append(('sale_id.user_id', 'in', self.user_ids.ids))

        datas = []
        fechas = []
        journals = []
        payment = self.env["account.payment"].search(domain,order='payment_reg asc')
        fechas.append({
            
            })
        total_amount = 0
        total_amount_ref = 0
        
        # Montos por método de pago:
        efectivo_usd = sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id != x.company_id.currency_id).mapped('amount_ref'))
        efectivo_bs  = sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id != x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id == x.company_id.currency_id).mapped('amount_ref'))
        banco_usd    = sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id != x.company_id.currency_id).mapped('amount_ref'))
        banco_bs     = sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id != x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id == x.company_id.currency_id).mapped('amount_ref'))

        if not payment:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        for invoices in payment:
            total_amount += round(invoices.amount,4) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,4)
            total_amount_ref += round(invoices.amount,4) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,4)
            datas.append({
                'date':    str(invoices.payment_reg.strftime("%d/%m/%Y")),
                'payment_id': invoices.name,
                'partner_id': invoices.partner_id.name,
                'journal_id': invoices.journal_id.name,
                'ref':    invoices.ref,
                'amount': round(invoices.amount,4) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,4),
                'currency_id': invoices.currency_id.name,
                'amount_ref': round(invoices.amount,4) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,4),
                'currency_id_ref': invoices.currency_id_ref.name,
            })
        moneda_diario = False
        for journal in payment.mapped('journal_id').sorted(lambda x: x.currency_id):
            moneda_diario = journal.currency_id if journal.currency_id else self.env.company.currency_id
            journals.append({
                'journal_id': journal.name,
                'journal_currency': moneda_diario.symbol,
                'monto_moneda_diario': 0 + sum(payment.filtered(lambda x: x.journal_id.id == journal.id and x.currency_id == moneda_diario).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.id == journal.id and x.currency_id != moneda_diario).mapped('amount_ref')),
            })

        # Array de fechas en función a los campos start_date y end_date:
        month_list = []
        current_date = self.start_date

        while current_date <= self.end_date:
            month_list.append(int(current_date.strftime('%m')))
            current_date += relativedelta(months=1)

            # Detener el bucle si current_date supera la fecha de fin
            if current_date.year == self.end_date.year and current_date.month > self.end_date.month:
                break

        # Añadir meses anteriores al mismo año
        if self.start_date.year == self.end_date.year:
            month_list = list(range(1, self.end_date.month + 1))

        # Añadir meses completos de años anteriores
        if self.start_date.year < self.end_date.year:
            for year in range(self.start_date.year + 1, self.end_date.year):
                month_list = list(range(1, 13)) + month_list
        
        # Agregando nuevos filtros para todas las fechas del año actual:
        current_year = date.today().year
        domain_all_months = [
            ('company_id', '=', self.company_id.id),
            ('payment_reg', '>=', date(current_year, 1, 1)),
            ('payment_reg', '<=', date(current_year, 12, 31)),
            ('state', '=', 'posted'),
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
            ('is_internal_transfer', '=', False)
        ]
        payment_all_months = self.env["account.payment"].search(domain_all_months,order='payment_reg asc')
        
        res = {
            'start_date':   str(self.start_date.strftime("%d/%m/%Y")),
            'end_date':     str(self.end_date.strftime("%d/%m/%Y")),
            'type_report': self.type_report,
            'company_name': self.company_id.name,
            'journal_id': ', '.join([str(i) for i in self.partner_ids.mapped('name')]),
            'company_vat':  self.company_id.vat,
            'invoices':     datas,
            'journals':     journals,
            'total_amount':round(total_amount,4),
            'total_amount_ref':round(total_amount_ref,4),
            # ==================================================================================== #
            'enero':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 1 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 1 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'febrero':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 2 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 2 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'marzo': round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 3 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 3 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'abril':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 4 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 4 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'mayo':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 5 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 5 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'junio':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 6 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 6 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'julio':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 7 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 7 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'agosto':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 8 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 8 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'septiembre':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 9 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 9 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'octubre':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 10 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 10 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'noviembre':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 11 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 11 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            'diciembre':round(sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 12 and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment_all_months.filtered(lambda x: int(x.payment_reg.month) == 12 and x.currency_id != x.company_id.currency_id).mapped('amount_ref')),4),
            # ==================================================================================== #       
            # Montos por método de pago:
            'efectivo_usd': round(efectivo_usd, 4),
            'efectivo_bs': round(efectivo_bs, 4),
            'banco_usd': round(banco_usd, 4),
            'banco_bs': round(banco_bs, 4),
            # Listado de meses:
            'month_list': month_list
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_account_reports.action_report_eu_reporte_payment_bank').report_action([],data=data)