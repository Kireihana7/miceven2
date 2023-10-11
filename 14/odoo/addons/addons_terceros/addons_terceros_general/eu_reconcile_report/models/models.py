# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import math
from odoo.exceptions import UserError
import operator



class AccountReportReconcile(models.TransientModel):
    _name = 'account.report.reconciles'
    _description = "Reconcile Report"

    from_date = fields.Date('Desde', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    to_date = fields.Date("Hasta", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    journal_ids = fields.Many2one('account.journal', string='Diario',
                               required=True,
                               domain="[('type', 'in', ('bank','cash'))]")
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    visibility =  fields.Selection([
        ("cabecera", 'Solo Resumen'),
        ("detalle", 'Solo Detalle'),
        ("todo", 'Detalle y Resumen'),
        ], string="¿Qué desea ver?",required=True)


    def print_report(self):
        domain = [
        ('company_id', '=', self.company_id.id),
        ('date', '>=', self.from_date),
        ('date', '<=', self.to_date),
        ('journal_id', '=', self.journal_ids.id),
        ]
        domain_saldo_inicial = [
        ('company_id', '=', self.company_id.id),
        ('date', '<', self.from_date),
        ('journal_id', '=', self.journal_ids.id),
        ]

        datas = []
        cabecera_saldo_inicial = self.env["account.bank.statement"].search([('journal_id','=',self.journal_ids.id),('date','<=',self.from_date)],limit=1,order="id asc").balance_start or 0.0
        lineas_saldo_inicial = self.env["account.bank.statement.line"].search(domain_saldo_inicial)
        acumulado = saldo_inicial = round(sum(lineas_saldo_inicial.mapped('amount')),2) + round(cabecera_saldo_inicial,2)
        acumulado_conciliado = saldo_inicial_conciliado = round(sum(lineas_saldo_inicial.filtered(lambda x: x.is_reconciled).mapped('amount')),2) + round(cabecera_saldo_inicial,2)
        acumulado_no_conciliado = saldo_inicial_no_conciliado = round(sum(lineas_saldo_inicial.filtered(lambda x: not x.is_reconciled).mapped('amount')),2)
        invoice = self.env["account.bank.statement.line"].search(domain,order='date asc')
        if not invoice:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        for invoices in invoice:
            acumulado += round(invoices.amount,2)
            acumulado_conciliado += round(invoices.amount if invoices.is_reconciled else 0.0,2)
            acumulado_no_conciliado += round(invoices.amount if not invoices.is_reconciled else 0.0,2)
            datas.append({
                'date':    invoices.date,
                'ref':    invoices.ref,
                'payment_ref': invoices.payment_ref,
                'partner_id': invoices.partner_id.name,
                'amount': round(invoices.amount,2),
                'acumulado': round(acumulado,2),
                'acumulado_conciliado': round(acumulado_conciliado,2),
                'acumulado_no_conciliado': round(acumulado_no_conciliado,2),
                'conciliado': 'Conciliado' if invoices.is_reconciled else 'No Concilicado'
                })
        res = {
            'start_date':   self.from_date,
            'end_date':     self.to_date,
            'company_name': self.company_id.name,
            'journal_id': self.journal_ids.name,
            'company_vat':  self.company_id.vat[:10]+'-'+self.company_id.vat[10:],
            'invoices':     datas,
            'saldo_inicial': round(saldo_inicial,2),
            'saldo_inicial_conciliado': round(saldo_inicial_conciliado,2),
            'saldo_inicial_no_conciliado': round(saldo_inicial_no_conciliado,2),
            'saldo_final': round(acumulado,2),
            'saldo_final_conciliado': round(acumulado_conciliado,2),
            'saldo_final_no_conciliado': round(acumulado_no_conciliado,2),
            'visibility':self.visibility,
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_reconcile_report.eu_reconcile_report').report_action([],data=data)