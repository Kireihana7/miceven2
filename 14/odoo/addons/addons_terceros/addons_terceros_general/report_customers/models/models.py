# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import math


class CustomerReport(models.TransientModel):
    _name = 'report.customer.sale'
    _description = "Customer Report"

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

    def print_report(self):
        domain = []
        datas = []

        invoice = self.env["sale.order"].search(
        [('state', '!=', 'draft'), 
        ('date_order', '>=', self.from_date),
        ('company_id', '=', self.company_id.id),
        ('date_order', '<=', self.to_date),
        ],
        order='partner_id asc')
        



        partner_ids = [] #listado de product_id unicos
        for invoices in invoice:
            # verifica si existe el producto en la lista
            if invoices.partner_id.id not in partner_ids:
                partner_ids.append(invoices.partner_id.id)

        #print(product_ids)
        for id in partner_ids:
            nombre = ''
            fecha = ''
            cliente_nombre = ''
            product_total = 0.0
            #print(id)
            for invoices in invoice:
                if id==invoices.partner_id.id:
                    fecha = invoices.date_order
                    cliente_nombre = invoices.partner_id.name
                    rif = invoices.partner_id.vat
                    nombre_factura = invoices.name
                    commercial=invoices.user_id.name
                    informations = '%s ' % invoices.partner_id.street if invoices.partner_id.street else ''
                    informations += '%s ' % invoices.partner_id.street2 if invoices.partner_id.street2 else ''
                    informations += '%s ' % invoices.partner_id.zip if invoices.partner_id.zip else ''
                    informations += ' ' if invoices.partner_id.zip and not invoices.partner_id.city else ''
                    informations += ' - ' if invoices.partner_id.zip and invoices.partner_id.city else ''
                    informations += '%s ' % invoices.partner_id.city if invoices.partner_id.city else ''
                    informations += '%s ' % invoices.partner_id.state_id.display_name if invoices.partner_id.state_id else ''
                    informations += '%s ' % invoices.partner_id.country_id.display_name if invoices.partner_id.country_id else ''

            datas.append({
                'name':cliente_nombre,
                'date':fecha,
                'rif_partner':rif,
                'invoice_name' :nombre_factura,
                'commercial' :commercial,
                'information' :informations,
                })   
                
        res = {
            'start_date': self.from_date,
            'end_date': self.to_date,
            'company_name': self.company_id.name,
            'company_vat': self.company_id.vat,
            'invoices': datas,
        }
        data = {
            'form': res,
        }
        return self.env.ref('report_customers.report_customers').report_action([],data=data)
