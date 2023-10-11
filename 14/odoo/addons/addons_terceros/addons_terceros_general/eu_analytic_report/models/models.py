# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import math
from odoo.exceptions import UserError
import operator

class AccountReportAnalytic(models.TransientModel):
    _name = 'account.report.analytic'
    _description = "Analytic Report"

    from_date = fields.Date('Desde', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    to_date = fields.Date("Hasta", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    analytic_id = fields.Many2one('account.analytic.account', string='Centro de Costo',required=True,)
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
        ('account_id', '=', self.analytic_id.id),
        ]
        domain_saldo_inicial = [
        ('company_id', '=', self.company_id.id),
        ('date', '<', self.from_date),
        ('account_id', '=', self.analytic_id.id),
        ]

        datas = []
        lineas_saldo_inicial = self.env["account.analytic.line"].search(domain_saldo_inicial)
        acumulado = saldo_inicial = round(sum(lineas_saldo_inicial.mapped('amount')),2)
        invoice = self.env["account.analytic.line"].search(domain,order='date asc')
        if not invoice:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        for invoices in invoice:
            acumulado += round(invoices.amount,2)
            datas.append({
                'date':    invoices.date,
                'ref':    invoices.ref,
                'partner_id': invoices.partner_id.name,
                'product_id': invoices.product_id.name,
                'unit_amount': invoices.unit_amount,
                'amount': round(invoices.amount,2),
                'acumulado': round(acumulado,2),
                })
        res = {
            'start_date':   self.from_date,
            'end_date':     self.to_date,
            'company_name': self.company_id.name,
            'account_id': self.analytic_id.name,
            'company_vat':  self.company_id.vat[:10]+'-'+self.company_id.vat[10:],
            'invoices':     datas,
            'saldo_inicial': round(saldo_inicial,2),
            'saldo_final': round(acumulado,2),
            'visibility':self.visibility,
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_analytic_report.eu_analytic_report').report_action([],data=data)