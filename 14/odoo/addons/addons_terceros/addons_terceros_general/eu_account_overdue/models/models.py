# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import math
from odoo.exceptions import UserError


class AttendanceReport(models.TransientModel):
    _name = 'account.report.overdue'
    _description = "Overdue Report"

    from_date = fields.Date('From Date', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    currency_id_company = fields.Many2one('res.currency', string="Moneda de la Compañia",
     default=lambda self: self.env.company.currency_id, invisible=True)
    currency_id = fields.Many2one('res.currency', string="Moneda de reporte",
     default=lambda self: self.env.company.currency_id,)
    journal_ids = fields.Many2many('account.journal', string='Journals',
        required=True,
        default=lambda self: self.env['account.journal'].search([('type', '=', 'sale')]))

    agrupar_clientes = fields.Boolean(
        string='Agrupar por Clientes',
    )

    def print_report(self):
        domain = []
        datas = []
        invoice = []
        codes = []
        clientes_ids = []
        cliente_dict = []
        if self.journal_ids:
            codes = [journal.id for journal in self.journal_ids]
        if self.from_date and self.to_date:
            invoice = self.env["account.move"].search(
            [('move_type', '=', 'out_invoice'), 
            ('state', '=', 'posted'), 
            ('date', '>=', self.from_date),
            ('company_id', '=', self.company_id.id),
            ('date', '<=', self.to_date),
            ('amount_residual', '>', 0),
            ('journal_id', 'in', codes)
            ],
            order='date asc')
        if not invoice:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        for invoices in invoice:
            por_vencer= 0.0
            dias_calle = 0
            vencido = 0.0
            dias_vencimiento = 0
            vencido_1_5 = 0
            vencido_6_10 = 0
            vencido_11_15 = 0
            vencido_16_20 = 0
            vencido_20 = 0
            dias_calle=abs(fields.Date.today() - invoices.invoice_date).days

            if invoices.partner_id.id not in clientes_ids:
                
                clientes_ids.append(invoices.partner_id.id)
                cliente_dict.append({
                    'id':invoices.partner_id.id,
                    'name':invoices.partner_id.name,
                })

            if self.company_id == self.currency_id_company:
                if fields.Date.today() > invoices.invoice_date_due:
                        # Vencido
                    vencido = invoices.amount_residual
                    dias_vencimiento=abs(fields.Date.today() - invoices.invoice_date_due).days
                    if dias_vencimiento>=1 and dias_vencimiento <=5:
                        vencido_1_5= invoices.amount_residual
                    if dias_vencimiento>=6 and dias_vencimiento <=10:
                        vencido_6_10= invoices.amount_residual
                    if dias_vencimiento>=11 and dias_vencimiento <=15:
                        vencido_11_15= invoices.amount_residual
                    if dias_vencimiento>=16 and dias_vencimiento <=20:
                        vencido_16_20= invoices.amount_residual
                    if dias_vencimiento>=21:
                        vencido_20= invoices.amount_residual
                if fields.Date.today() <= invoices.invoice_date_due:
                    # Por VENCER
                    por_vencer = invoices.amount_residual
            else:
                if fields.Date.today() > invoices.invoice_date_due:
                        # Vencido
                    vencido = invoices.amount_residual_signed_ref
                    dias_vencimiento=abs(fields.Date.today() - invoices.invoice_date_due).days
                    if dias_vencimiento>=1 and dias_vencimiento <=5:
                        vencido_1_5= invoices.amount_residual_signed_ref
                    if dias_vencimiento>=6 and dias_vencimiento <=10:
                        vencido_6_10= invoices.amount_residual_signed_ref
                    if dias_vencimiento>=11 and dias_vencimiento <=15:
                        vencido_11_15= invoices.amount_residual_signed_ref
                    if dias_vencimiento>=16 and dias_vencimiento <=20:
                        vencido_16_20= invoices.amount_residual_signed_ref
                    if dias_vencimiento>=21:
                        vencido_20= invoices.amount_residual_signed_ref
                if fields.Date.today() <= invoices.invoice_date_due:
                    # Por VENCER
                    por_vencer = invoices.amount_residual_signed_ref
            datas.append({
                'nombre_vendedor':invoices.invoice_user_id.name,
                'id_cliente':invoices.partner_id.id,
                'codigo_cliente':invoices.partner_id.code,
                'nombre_cliente':invoices.invoice_partner_display_name,
                'name':invoices.name,
                'fecha_emision':invoices.invoice_date,
                'fecha_venci':invoices.invoice_date_due,
                'amount_total':invoices.amount_total if self.currency_id == self.currency_id_company else invoices.amount_ref,
                'amount_residual':invoices.amount_residual if self.currency_id == self.currency_id_company else invoices.amount_residual_signed_ref ,
                'por_vencer':por_vencer,
                'vencido':vencido,
                'vencido_1_5':vencido_1_5,
                'vencido_6_10':vencido_6_10,
                'vencido_11_15':vencido_11_15,
                'vencido_16_20':vencido_16_20,
                'vencido_20':vencido_20,
                'dias_vencimiento':dias_vencimiento,
                'dias_calle':dias_calle,
                })
        res = {
            'start_date': self.from_date,
            'end_date': self.to_date,
            'company_name': self.company_id.name,
            'company_vat': self.company_id.vat,
            'invoices': datas,
            'currency_id': self.currency_id,
            'currency_id_label': self.currency_id.currency_unit_label,
            'clientes_ids':clientes_ids,
            'cliente_dict':cliente_dict,
            'agrupar_clientes':self.agrupar_clientes,
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_account_overdue.account_overdue_print').report_action([],data=data)