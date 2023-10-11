# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools
from datetime import datetime
from odoo.exceptions import  UserError

    
class SkitBankReconcilReport(models.AbstractModel):
    _name = "report.skit_bank_reconcil.reconcil_report"



    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        if(data.get('skit_report_type') == 'pdf'):
            journal_id = data.get('journal_id')
            date_from = data.get('date_from')
            date_to = data.get('date_to')
        else:
            journal_id = data['form']['journal_id'][0]
            date_from = data['form']['date_from']
            date_to = data['form']['date_to']
        journal = self.env['account.journal'].search([('id','=', journal_id)])
        last_bank_stmt = self.env['account.bank.statement'].search([('journal_id', '=', journal.id)], order="date desc, id desc", limit=1)
        last_balance = last_bank_stmt and last_bank_stmt[0].balance_end or 0
        
        gl_code = journal.default_account_id.name
        default_debit_acc_id = journal.payment_debit_account_id.id
        
        #Virtual GL Balance:
        account_ids = tuple(filter(None, [journal.payment_debit_account_id.id, journal.payment_credit_account_id.id]))
        amount_field = 'balance' if (not journal.currency_id or journal.currency_id == journal.company_id.currency_id) else 'amount_currency'
        current_balance = 0
        ids =str(account_ids)
        if account_ids:
            query = """SELECT sum("""+amount_field+""") FROM account_move_line WHERE account_id in """+(ids)
            list=[]
            list.append(account_ids)
            if date_from:
                date_frompara = "'"+date_from+"'"
                query = query+(""" AND date >="""+date_frompara)
                list.append(date_from)
            if date_to:
                date_toparam = "'"+date_to+"'"
                query=query+(""" AND date <=""" +date_toparam)
                list.append(date_to)
            self.env.cr.execute(query, [],)
            query_results = self.env.cr.dictfetchall()
            if query_results and query_results[0].get('sum') != None:
                current_balance = query_results[0].get('sum')
        self.env.cr.execute("""SELECT COALESCE(SUM(aml.balance),0) 
                        FROM account_move am join account_move_line aml on aml.move_id = am.id where aml.statement_line_id  
                        IN (SELECT line.id 
                            FROM account_bank_statement_line AS line 
                            LEFT JOIN account_bank_statement AS st 
                            ON line.statement_id = st.id 
                            WHERE st.journal_id = %s and st.state = 'open')""", (journal.id,))
        already_reconciled = self.env.cr.fetchone()[0]
        self.env.cr.execute("""SELECT COALESCE(SUM(AMOUNT),0) 
                            FROM account_bank_statement_line AS line 
                            LEFT JOIN account_bank_statement AS st 
                            ON line.statement_id = st.id 
                            WHERE st.journal_id = %s and st.state = 'open'""", (journal.id,))
        all_lines = self.env.cr.fetchone()[0]
        virtual_gl_balance = all_lines - already_reconciled
        
        #Unreconciled Bank Statement Lines
        journal_id = str(journal.id)
        company_id = str(self.env.user.company_id.id)
        unreconcile_line = """(select 1 from account_move am join account_move_line aml on aml.move_id = am.id where aml.statement_line_id  = stl.id) """ 
        if date_to: 
            date_toparam = "'"+date_to+"'"
            unreconcile_line =  """(select 1 from account_move am join account_move_line aml on aml.move_id = am.id where aml.statement_line_id  = stl.id and  date_maturity<"""+date_toparam+""")""" 
            
        sql_query = """SELECT stl.id 
                        FROM account_bank_statement st inner join account_move_line aml on st.journal_id=aml.journal_id
                        INNER JOIN account_bank_statement_line stl on st.id = stl.move_id 
                        where aml.account_id IS NULL AND st.journal_id= """+journal_id+""" AND aml.reconciled_date IS NULL                        
                        AND st.company_id= """+company_id+""" AND not exists """+unreconcile_line+""" """
                    
        list=[]
        list.append({'journal_id':journal.id,'company_id' :self.env.user.company_id.id,})
        if date_from:
            date_fromparam = "'"+date_from+"'"
            sql_query = sql_query+(""" AND aml.statement_date >="""+date_fromparam)
            list.append(date_from)
        if date_to: 
            date_toparam = "'"+date_to+"'"
            sql_query=sql_query+(""" AND aml.statement_date <="""+date_toparam)
            list.append(date_to)
        sql_query += """ GROUP BY stl.id"""
        
        #raise UserError(sql_query)
        self.env.cr.execute(sql_query, [],)
        st_lines_left = self.env['account.bank.statement.line'].browse([line.get('id') for line in self.env.cr.dictfetchall()])
        
        #Validated Payments not linked with a Bank Statement Line
        domain_checks_to_print = [
                                  ('account_id', '=', default_debit_acc_id),
                                  ('full_reconcile_id','=', False), 
                                  ('statement_id','=',False),            
            
        ]
        if date_from:
            domain_checks_to_print.append(('reconciled_date', '>=', date_from),)
        if date_to:
            domain_checks_to_print.append(('reconciled_date', '>', date_to),)
            #print (date_to)
        pay_move_line = self.env['account.move.line'].search(domain_checks_to_print)
        
        payment_lines=[]
        for pay in pay_move_line:
                pay_dict = {}
                pay_dict['name']=pay.name if pay.name else pay.ref
                pay_dict['payment_date']=pay.date
                pay_dict['ref']=pay.move_id.name
                pay_dict['amount']=pay.balance
            
                payment_lines.append(pay_dict)
        
        return {
        'ids': [],
        'model': 'account.move.line',
        'docs': pay_move_line,
        'data':data,
        'current_balance':current_balance,
        'default_debit_acc_id':default_debit_acc_id,
        'gl_code':gl_code,
        'last_balance':last_balance,
        'payment_lines':payment_lines,
        'virtual_gl_balance': virtual_gl_balance,
        'st_lines_left':st_lines_left,
        'data': dict(
                data,
                journal= journal,
            ),
        }



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    reconciled_date = fields.Datetime(string='Reconciled Date')
    statement_date = fields.Datetime(string='statement Date')   
    
    
    #@api.multi
    def create(self,vals):
        #super(AccountMoveLine,self).create(vals)
        #if vals.get('date_maturity'):
            #vals['statement_date'] =vals.get('date_maturity')
        records  = super(AccountMoveLine,self).create(vals)
        for res in records:
            #print (res)
            vals=[]
            statement_date = self.env['account.bank.statement'].browse(res.statement_id.id)
            if res.date or statement_date:
                #res.statement_date = datetime.strftime(statement_date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
                #res.reconciled_date= datetime.strftime(res.date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
                r_date = datetime.strftime(res.date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
                if(statement_date):
                    s_date = datetime.strftime(statement_date.date, '%Y-%m-%d %H:%M:%S')
                else:
                    s_date = False
                records.write({'statement_date': s_date,
                               'reconciled_date': r_date})
               
        return records;
    
    
#===============================================================================
#     @api.multi
#     def write(self,vals):
# #         super(AccountMoveLine,self).write(vals)
# #         if vals.get('date'):
# #             vals['statement_date'] =vals.get('date')
# #         super(AccountMoveLine,self).write(vals)
#         
#         
#         if self.date or vals.get('date'):
#                 vals['statement_date']= datetime.strftime(self.date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
#                 vals['reconciled_date']= datetime.strftime(self.date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
#         res  = super(AccountMoveLine,self).write(vals)
#                 #print (res.statement_date)
#                 #print (res.reconciled_date)
#===============================================================================
 
    
        