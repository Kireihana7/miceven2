# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class EstadoCuenta(models.TransientModel):
    _name = 'estado.cuenta'
    _description = 'Estado de cuentas'

    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Proveedor / Cliente')
    company_id = fields.Many2one('res.company', string='Compañia', required=True,
                                 default=lambda self: self.env.company)
    tipo_cuenta = fields.Selection([('cuenta_x_pagar', 'Cuentas por Pagar'), ('cuenta_x_cobrar', 'Cuentas por Cobrar')], default='cuenta_x_pagar', required = True)

    def report_estado_cuenta(self):
        final = []
        domain =  [
            ('company_id', '=', self.company_id.id)]

        proveedor = []
        domain_two = [] # DOMAIN PARA ACCOUNT MOVE
        domain_tree = [] # DOMAIN PARA ACCOUNT PAYMENT
        domain_four = [] # DOMAIN PARA ACCOUNT PAYMENT
        domain_five = [] # DOMAIN PARA ACCOUNT PAYMENT
        payment_type = ''
        
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        if self.tipo_cuenta == 'cuenta_x_pagar':
            domain_two += [('state','=','posted'),('move_type','in',('in_invoice','in_refund'))]
            domain_tree += [('state','=','posted'),('free_payment','!=',False),('payment_type','=','outbound')]
        if self.tipo_cuenta == 'cuenta_x_cobrar':
            domain_two += [('state','=','posted'),('move_type','=','out_invoice')]
            domain_tree += [('state','=','posted'),('free_payment','!=',False),('payment_type','=','inbound')]

        account_move = self.env['account.move'].search(domain).mapped('partner_id')

        if len(account_move)==0:
            raise UserError(_("No hay datos para imprimir"))



        for account in account_move:
            if account and account.id not in proveedor:
                proveedor.append(account.id)
                domain_four = domain_two + [(('partner_id','=',account.id))]
                domain_five = domain_tree + [(('partner_id','=',account.id))]
                
                c1 = sum(self.env['account.move'].search(domain_four).mapped('amount_residual'))
                c1usd = sum(self.env['account.move'].search(domain_four).mapped('amount_residual_signed_ref'))                
                c2 = sum(self.env['account.payment'].search(domain_five).mapped('monto_disponible'))                
                account_move_two = self.env['account.payment'].search(domain_five)
                
                c2usd = 0.0
                for am in account_move_two:
                    if am.currency_id.id == 3:
                        c2usd += am.monto_disponible*am.manual_currency_exchange_rate
                    else:
                        c2usd += am.monto_disponible/am.manual_currency_exchange_rate
                
                c3 = c1 - c2
                c4 = c1usd - c2usd
                final.append({
                    'name' : account.name,
                    'c1' : c1,
                    'c2' : c2,
                    'c1usd' : c1usd,
                    'c2usd' : c2usd,
                    'c3' : c3,
                    'c4' : c4,
                    })
        #raise UserError(domain_four)

        res = {
            'model': self._name,
            'invoices': final,
            'date_start': self.date_start if self.date_start else '',
            'date_end': self.date_end if self.date_end else '',
            'partner_id_vat': self.partner_id.vat if self.partner_id.vat else '',
            'partner_id_name': self.partner_id.name if self.partner_id.name else '',
            'tipo': 'CUENTAS POR PAGAR' if self.tipo_cuenta == 'cuenta_x_pagar' else 'CUENTAS POR COBRAR',
        }
        
        data = {
            'form': res,
        }

        return self.env.ref('eu_estado_cuenta.estado_cuenta_report').report_action(self, data=data)