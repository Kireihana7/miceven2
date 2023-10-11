# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo.exceptions import UserError, ValidationError
import math


class CustomerReport(models.TransientModel):
    _name = 'report.customer.sale'
    _description = "Customer Report"

    from_date = fields.Datetime('From Date', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    to_date = fields.Datetime("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)

    state = fields.Selection([
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo')], string="State")
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )

    def print_report(self):
        datas = []

        domain = []

        if self.from_date:
            domain.append(('create_date', '>=', self.from_date))
        if self.to_date:
            domain.append(('create_date', '<=', self.to_date))
        if self.state:
            domain.append(('state', '=', self.state))
        else:
            domain.append(('state', 'in', ('activo', 'inactivo')))

        partners = self.env['res.partner'].search(domain)

        if len(partners) == 0:
            raise UserError(_('No hay datos para imprimir'))
        else:
            estatus = ''
            for rec in partners:
                if rec.state == 'activo':
                    estatus = 'Activo'
                elif rec.state == 'inactivo':
                    estatus = 'Inactivo'
                cliente_nombre = rec.name
                rif = rec.vat
                commercial=rec.user_id.name
                state=estatus
                informations = '%s ' % rec.street if rec.street else ''
                informations += '%s ' % rec.street2 if rec.street2 else ''
                informations += '%s ' % rec.zip if rec.zip else ''
                informations += ' ' if rec.zip and not rec.city else ''
                informations += ' - ' if rec.zip and rec.city else ''
                informations += '%s ' % rec.city if rec.city else ''
                informations += '%s ' % rec.state_id.display_name if rec.state_id else ''
                informations += '%s ' % rec.country_id.display_name if rec.country_id else ''

                datas.append({
                    'name':cliente_nombre,
                    'rif_partner':rif,
                    'state':state,
                    'commercial' :commercial,
                    'information' :informations,
                    })
                
        res = {
            'start_date': self.from_date.date() if self.from_date else '',
            'end_date': self.to_date.date() if self.to_date else '',
            'state': self.state if self.state else '',
            'company_name': self.company_id.name,
            'company_vat': self.company_id.vat,
            'partners': datas,
        }

        data = {
            'form': res,
        }
        return self.env.ref('eu_partner_approve.report_customers').report_action([],data=data)
