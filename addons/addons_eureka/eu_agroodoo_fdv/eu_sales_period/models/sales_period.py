# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class SalesPeriod(models.TransientModel):
    _name = 'sales.period'

    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    company_id = fields.Many2one('res.company', string='Compañia', required=True,
                                 default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', string='Diarios', domain="[('type', '=', 'sale')]")

    def report_sales_period(self):
        final = []
        domain =  [
            ('company_id', '=', self.company_id.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted')]

        if self.journal_id:
            domain.append(('journal_id', '=', self.journal_id.id))
        if self.date_start:
            domain.append(('invoice_date', '>=', self.date_start))
        if self.date_end:
            domain.append(('invoice_date', '<=', self.date_end))

        account_move = self.env['account.move'].search(domain)
            
        if len(account_move)==0:
            raise UserError(_("No hay datos para imprimir"))

        for row in account_move:
            payment_term = 'contado'
            if row.invoice_date_due > row.invoice_date:
                payment_term = 'credito'

            final.append({
                'name': row.name,
                'date': row.invoice_date,
                'partner_id': row.partner_id.name,
                'amount_untaxed': row.amount_untaxed,
                'amount_tax': row.amount_tax,
                'amount_total': row.amount_total,
                'company_id': row.company_id,
                'payment_term': payment_term,
                })            

        res = {
            'ids': self.ids,
            'model': self._name,
            'invoices': final,
            'journal_id': self.journal_id.name if self.journal_id else '',
            'date_start': self.date_start if self.date_start else '',
            'date_end': self.date_end if self.date_end else '',
            'partner_id_vat': self.partner_id.vat if self.partner_id.vat else '',
            'partner_id_name': self.partner_id.name if self.partner_id.name else '',
        }
        
        data = {
            'form': res,
        }

        return self.env.ref('eu_sales_period.sales_period_report').report_action(self, data=data)
