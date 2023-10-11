# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import math
from odoo.exceptions import UserError


class AccountHistorialDocument(models.TransientModel):
    _name = 'account.historial.document'
    _description = "Overdue Report"

    hasta = fields.Date("Hasta", required=True)
    company_id = fields.Many2one('res.company',string='Compañía',required=True,default=lambda self: self.env.company.id,copy=True,readonly=1)
    tipo = fields.Selection(string='Tipo de cuenta', selection=[('receivable','Por cobrar'),('payable','Por pagar')])
    journal_ids = fields.Many2many('account.journal', string='Diarios',required=False)
    partner_id = fields.Many2one('res.partner', string='Contacto',required=False)
    check = fields.Boolean('Con detalles', defalut=False)
    def _domain_branch_ids(self):
        return [('id','in',(self.env.user.branch_ids.ids))]
    branch_ids = fields.Many2many('res.branch', string='Sucursales',required=True,
                                   default=lambda self: self.env.user.branch_ids,domain=_domain_branch_ids)

    
    def print_report(self):
        datas = []
        document = []
        codes = []
        monto=0
        journals = []
        branches = []
        domain = [
            ('state', '=', 'posted'), 
            ('company_id', '=', self.company_id.id),
            ('date', '<=', self.hasta),
        ]

        if self.journal_ids:
            codes = [journal.id for journal in self.journal_ids]
            domain += [('journal_id', 'in', codes)]

        if self.partner_id:
            domain += [('partner_id', '=', self.partner_id.id)]
        
        document = self.env["account.move"].search(domain,
            order='date asc')

        if not document:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')

        for partner in document.mapped('partner_id'):
            monto =  sum(document.filtered(lambda x: x.partner_id.id == partner.id).mapped('line_ids').filtered(lambda y: y.account_id.user_type_id.type == self.tipo).mapped('balance'))
            credit_debit = document.filtered(lambda c: c.partner_id.id == partner.id).mapped('line_ids').filtered(lambda y: y.account_id.user_type_id.type == self.tipo)
            balance= 0
            if self.check:
                for line in credit_debit:
                    if monto !=0 and len(line) > 0:
                        balance += line.balance
                        datas.append({
                            'contacto':partner.name,
                            'monto': monto,
                            'credit': line.credit,
                            'debit': line.debit,
                            'nombre':line.move_id.name,
                            'balance':balance,
                        })
            else:
               datas.append({
                    'contacto':partner.name,
                    'monto': monto,
                }) 

        if len(datas)==0:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        
        for diario in self.journal_ids :
            if diario:
                journals.append({
                    'the_journal': diario.name
                })
        
        for branch in self.branch_ids :
            if branch:
                branches.append({
                    'the_branch': branch.name
                })
        tipo = ''
        if self.tipo == 'receivable':
            tipo = 'Por cobrar'
        if self.tipo == 'payable' :
            tipo = 'Por pagar'

        res = {
            'hasta': (self.hasta).strftime('%d/%m/%Y'),
            'company_name': self.company_id.name,
            'company_logo': self.company_id.logo,
            'company_vat': self.company_id.rif,
            'documents': datas,
            'journal_ids': journals if self.journal_ids else False,
            'branch_ids': branches if self.branch_ids else False,
            'tipo': tipo,
            'check': self.check,
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_accounting_document.custom_action_report_accounting_doc').report_action([],data=data)