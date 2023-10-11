# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import math
from odoo.exceptions import UserError
import operator
import pytz
import datetime



class BalanceComprobacion(models.TransientModel):
    _name = 'balance.comprobacion'
    _description = "Legal Daily Report"

    company_id = fields.Many2one('res.company', string='Compañia', required=True,
                                 default=lambda self: self.env.company)
    fiscalyear_id = fields.Many2one('account.fiscal.year', string='Año fiscal')
    date_from = fields.Date(string='Fecha inicio', required= True)
    date_to = fields.Date(string='Fecha fin', required= True)
    target_move = fields.Selection([('posted', 'Entradas publicadas'),
                                    ('all', 'Todas las entradas'),
                                    ], string='Movimientos', required=True,
                                    default='posted')
    display_account = fields.Selection([('all', 'Todas'),
                                        ('movement', 'Con movimientos'),
                                        ],
                                        string='Mostrar cuentas', required=True, 
                                        default='all')
    show_initial_balance = fields.Boolean(string='Mostrar saldo inicial (Libro Mayor)', default= True)

    parent_1 = fields.Many2one('account.account', string='Grupo desde',)
    parent_2 = fields.Many2one('account.account', string='Grupo hasta',)

    hora_actual = fields.Char(string="Hora actual",compute="_hora_pesaje")
    
    def _hora_pesaje(self):
        self.hora_actual = (datetime.datetime.now()).astimezone(pytz.timezone(self.env.user.tz)).strftime('%I:%M %p')

    @api.onchange('date_to')
    def onchange_date_to(self):
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise UserError(_('La fecha de finalización debe ser mayor que la fecha de inicio.'))

    @api.onchange('parent_1')
    def onchange_parent_1(self):
        if self.parent_2.code and self.parent_1.code and self.parent_1.code > self.parent_2.code:
            raise UserError(_('La cuenta de incio debe ser menor a la de finalización.'))

    @api.onchange('parent_2')
    def onchange_parent_2(self):
        if self.parent_1.code and self.parent_2.code and self.parent_2.code < self.parent_1.code:
            raise UserError(_('La cuenta de finalización debe ser mayor a la de inicio.'))

    def print_report(self):

        datas = []

        #domain =  [('company_id', '=', self.company_id.id)]

        #if self.parent_1:
        #    domain.append(('id', 'child_of', self.parent_1.id))
        #if self.parent_2:
        #    domain.append(('id', 'child_of', self.parent_2.id))
        
        account = self.env["account.account"].search([('company_id', '=', self.company_id.id)])

        if not account:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        for acc in account:
            debit_final = 0
            credit_final = 0
            balance_final = 0
            balance_final_total = 0

            debit_initial = 0
            credit_initial = 0
            balance_initial = 0
            resultado_periodo = 0
            saldo_final = 0

            account_code = acc.code
            account_name = acc.name
            parent = acc.parent_path            

            child = self.env["account.account"].search([('id','child_of',[acc.id])])

            for chi in child:
                for child_line in chi.move_line_ids.mapped(lambda x: {'debit':x.debit,'credit':x.credit,'state':x.parent_state,'date':x.date}):
                    if child_line['state'] != 'posted': continue
                    #SI HAY FECHAS
                    if self.date_from:
                        if self.show_initial_balance == True:
                            if child_line['date'] < self.date_from:
                                debit_initial   += child_line['debit']
                                credit_initial  += child_line['credit']
                                balance_initial += (child_line['debit']-child_line['credit'])

                        if child_line['date'] >= self.date_from and child_line['date'] <= self.date_to:
                            
                            if self.target_move == 'all':
                                debit_final += child_line['debit']
                                credit_final += child_line['credit']
                                balance_final = (debit_final - credit_final)

                            if self.target_move == 'posted':
                                debit_final += child_line['debit']
                                credit_final += child_line['credit']
                                balance_final = (debit_final - credit_final)

            balance_final_total += (balance_initial+balance_final)

            if self.display_account == 'movement':
                if balance_initial !=0 or balance_final != 0:

                    datas.append({
                        'account_code':             account_code,
                        'account_name':             account_name,
                        'debit_final':              debit_final,
                        'credit_final':             credit_final,
                        'balance_final':            balance_final,
                        'balance_final_total':      balance_final_total,
                        'debit_initial' :           debit_initial,
                        'credit_initial' :          credit_initial,
                        'balance_initial' :         balance_initial,
                        'parent' :                  parent,
                        })
            else:
                datas.append({
                    'account_code':             account_code,
                    'account_name':             account_name,
                    'debit_final':              debit_final,
                    'credit_final':             credit_final,
                    'balance_final':            balance_final,
                    'balance_final_total':      balance_final_total,
                    'debit_initial' :           debit_initial,
                    'credit_initial' :          credit_initial,
                    'balance_initial' :         balance_initial,
                    'parent' :                  parent,
                    })


        datas = sorted(datas, key= operator.itemgetter('account_code'), reverse=False)
        res = {
            'start_date':           self.date_from,
            'end_date':             self.date_to,
            'hora_actual':          self.hora_actual,
            'company_name':         self.company_id.name,
            'company_id':           self.company_id.id,
            'currency_id':          self.company_id.currency_id.symbol,
            'company_vat':          self.company_id.rif if self.company_id.rif else '',
            'invoices':             datas,
            'target_move':          self.target_move,
            'display_account':      self.display_account,
            'show_initial_balance': self.show_initial_balance,
        }

        #raise UserError(self.company_id.id)
        data = {
            'form': res,
        }


        #resultado del peridoo
        #debe - haber

        #saldo final
        #saldo anterior + saldo final
        return self.env.ref('eu_balance_comprobacion.eu_balance_comprobacion').report_action([],data=data)
