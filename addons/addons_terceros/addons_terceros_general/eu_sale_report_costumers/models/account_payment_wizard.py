
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class AccountPaymentWizard(models.TransientModel):
    _name = 'report.account.payment.wizard'
    _description = 'Report account payment'


    desde = fields.Date('Desde', required=True)
    hasta = fields.Date('Hasta', required=True)
    currency_id = fields.Many2one('res.currency', String="Moneda a Filtrar")
    report_currency = fields.Selection([
        ('usd', 'Dolár'),
        ('vef', 'Bolívar')
    ], String="Moneda a Reportar", required=True)
    partner_id = fields.Many2many('res.partner', String="Cliente")
    journal_id = fields.Many2one('account.journal', String="Diario")

    def print_report(self):
        data = []
        domain = [
            ('state','=','posted'),
            ('date','>=',self.desde),
            ('date','<=',self.hasta),
            ('partner_type','=','customer'),
            ('payment_type','=','inbound'),
        ]

        if self.currency_id:
            domain.append(('currency_id','=', self.currency_id.id)) 
        
        if self.journal_id:
            domain.append(('journal_id','=', self.journal_id.id))

        if self.partner_id:
            domain.append(('partner_id','in', self.partner_id.ids))

        payments  = self.env['account.payment'].search(domain)
        amount_bs  = sum(payments.filtered(lambda x: x.currency_id != x.company_id.currency_id).mapped('amount')) + sum(payments.filtered(lambda x: x.currency_id == x.company_id.currency_id).mapped('amount_ref'))
        amount_usd  = sum(payments.filtered(lambda x: x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payments.filtered(lambda x: x.currency_id != x.company_id.currency_id).mapped('amount_ref'))

        if len(payments) == 0:
            raise UserError("NO hay registros con el filtro seleccionado entre estas fechas...!")

        for payment in payments:
            data.append({
                'numero': payment.name,
                'fecha': payment.date.strftime('%d/%m/%Y'),
                'partner_id': payment.partner_id.name,
                'ref': payment.ref,
                'journal_code': payment.journal_id.code,
                'num_cuenta': payment.journal_id.bank_account_id.acc_number,
                'tasa_manual': "{0:.4f}".format(payment.manual_currency_exchange_rate),
                'monto_bs': round(payment.amount if payment.currency_id != payment.company_id.currency_id else payment.amount_ref,2),
                'monto_usd': round(payment.amount if payment.currency_id == payment.company_id.currency_id else payment.amount_ref,2),
                'moneda': int(payment.currency_id.id),
                'fecha_efectiva': payment.payment_reg.strftime('%d/%m/%Y'),
            })
            
            sorted(data, key=lambda x: x['fecha'])
            
        res={
            'desde': self.desde.strftime('%d/%m/%Y'),
            'hasta':self.hasta.strftime('%d/%m/%Y'),
            'docs': data,
            'amount_bs':amount_bs,
            'amount_usd':amount_usd,
            'currency_id': 'USD' if self.currency_id.name == 'USD' else 'VEF',
            'report_currency': 'USD' if self.report_currency == 'usd' else 'VEF',

        }

        data = {
            'form': res
        }

        return self.env.ref('eu_sale_report_costumers.custom_action_cobros_por_numero_multimoneda_wizard').report_action(self,data=data)
  