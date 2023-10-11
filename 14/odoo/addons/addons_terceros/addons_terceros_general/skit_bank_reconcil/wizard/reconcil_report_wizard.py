# -*- coding: utf-8 -*-
from odoo import api, models, fields

    
class skit_reconcil_report(models.TransientModel):
    _name = "bank.reconcil.rep"
    
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    journal_id = fields.Many2one('account.journal',
                                    domain=[('type', 'in', ('bank','cash'))],
                                    string='Journal',
                                    help="The accounting journal corresponding to this bank account.")
    #@api.multi
    def print_report(self):
        active_ids = self.env.context.get('active_ids', [])
        journal_id = self.journal_id.id
        date_from =self.date_from
        date_to =self.date_to
        datas = {
        'ids': active_ids,
        'model': 'account.payment',
        'form': self.read(),
        'journal_id':journal_id,
        'date_from':date_from,
        'date_to':date_to,
        'skit_report_type': 'pdf'
        }
        return self.env.ref('skit_bank_reconcil.bank_reconciliation_report').report_action(self, data=datas)

    def _build_contexts(self, data):
        result = {}
        result['date_from'] = 'date_from' in data['form'] and data['form']['date_from'] or False
        result['date_to'] = 'date_to' in data['form'] and data['form']['date_to'] or False
        result['journal_id'] = 'journal_id' in data['form'] and data['form']['journal_id'] or False
        return result
    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('skit_bank_reconcil.bank_reconciliation_report').report_action(records, data=data)
 
    #@api.multi
    def check_report_xlsx(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        data['skit_report_type'] = "XLS"
        data['skit_currency'] = self.env.user.currency_id.symbol
        return self._print_report(data)
      
    



