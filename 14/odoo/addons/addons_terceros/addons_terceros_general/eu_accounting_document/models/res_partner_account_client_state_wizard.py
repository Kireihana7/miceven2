from email.policy import default
from tokenize import String
from odoo import models, api,fields
from odoo.exceptions import UserError

class ResPartnerAccountClientStateWizard(models.TransientModel) :
    _name = 'res.partner.account.client.state.wizard'

    desde = fields.Date(String="Desde", required=True)
    hasta = fields.Date(String="Hasta", required=True)
    company_id = fields.Many2one('res.company',string='Compañía',required=True,default=lambda self: self.env.company.id,copy=True,readonly=1)
    partner_id = fields.Many2one('res.partner', string='Contacto',required=False, )
    currency_id = fields.Many2one('res.currency', String='Moneda',default=lambda self: self.env.company.currency_id.id)
    tipo = fields.Selection(string='Tipo de cuenta', selection=[('receivable','Por cobrar'),('payable','Por pagar')])

    def print_report_client_account_state(self):
        datas = []
        document = []
        monto=0
        domain = [
            ('state', '=', 'posted'), 
            ('company_id', '=', self.company_id.id),
            ('partner_id', '=', self.partner_id.id),
            ('date', '<=', self.desde),
        ]
        domain_two = [
            ('state', '=', 'posted'), 
            ('company_id', '=', self.company_id.id),
            ('partner_id', '=', self.partner_id.id),
            ('date', '<=', self.hasta),
            ('date', '>', self.desde),
        ]

        if self.partner_id:
            domain += [('partner_id', '=', self.partner_id.id)]
        
        document = self.env["account.move"].search(domain_two,
            order='date asc')

        document_from = self.env["account.move"].search(domain,
            order='date asc')

        if not document:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        balance= 0
        total_debit = 0
        total_credit = 0
        inicial = document_from.filtered(lambda x: x.partner_id.id == self.partner_id.id)
        saldo_inicial = 0
        balance_ini = 0
        for ini in inicial:
            balance_ini = sum(ini.mapped('line_ids').filtered(lambda y: y.account_id.user_type_id.type == 'receivable').mapped('balance'))
            saldo_inicial += balance_ini if self.currency_id == self.env.company.currency_id else (balance_ini * ini.manual_currency_exchange_rate)
        balance = balance + balance_ini
        for partner in document.mapped('partner_id'):
            monto =  sum(document.filtered(lambda x: x.partner_id.id == partner.id).mapped('line_ids').filtered(lambda y: y.account_id.user_type_id.type == 'receivable').mapped('balance'))
            credit_debit = document.filtered(lambda c: c.partner_id.id == partner.id).mapped('line_ids').filtered(lambda y: y.account_id.user_type_id.type == 'receivable')
            
            for line in credit_debit:
                if monto !=0 and len(line) > 0:
                    balance += line.balance if self.currency_id == self.company_id.currency_id else (line.balance * line.move_id.manual_currency_exchange_rate)
                    datas.append({
                        'monto': monto,
                        'credit': line.credit if self.currency_id == self.company_id.currency_id else line.credit * line.move_id.manual_currency_exchange_rate,
                        'debit': line.debit if self.currency_id == self.company_id.currency_id else line.debit * line.move_id.manual_currency_exchange_rate,
                        'nombre':line.move_id.name,
                        'balance':balance,
                        'emision':(line.move_id.invoice_date).strftime('%d/%m/%Y'),
                        'vencimiento':(line.move_id.invoice_date_due or line.move_id.invoice_date).strftime('%d/%m/%Y'),
                    })
                    total_debit += line.debit if self.currency_id == self.company_id.currency_id else line.debit * line.move_id.manual_currency_exchange_rate
                    total_credit += line.credit if self.currency_id == self.company_id.currency_id else line.credit * line.move_id.manual_currency_exchange_rate
        
        if len(datas)==0:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')
        
        res = {
            'desde': (self.desde).strftime('%d/%m/%Y'),
            'hasta': (self.hasta).strftime('%d/%m/%Y'),
            'contacto': self.partner_id.name,
            'cedula': self.partner_id.cedula,
            'rama': self.partner_id.branch_id.name,
            'company_name': self.company_id.name,
            'company_logo': self.company_id.logo,
            'company_vat': self.company_id.rif,
            'documents': datas,
            'saldo_inicial': saldo_inicial,
            'currency_id': self.currency_id.name,
            'total_debit':total_debit,
            'total_credit':total_credit,
            'vendedor': self.partner_id.user_id.name,
            'balance':balance + balance_ini,
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_accounting_document.custom_action_report_client_account_state').report_action([],data=data)