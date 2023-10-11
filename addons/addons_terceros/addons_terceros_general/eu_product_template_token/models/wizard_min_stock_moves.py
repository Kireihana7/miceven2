from odoo import api, models, modules,fields
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
TODAY = fields.Datetime.now()

class WizMinStockMoves(models.TransientModel):
    _name="wiz.min.stock.moves"


    def company_domains(self):
        for rec in self:
            return [('id','in',rec.env.user.company_ids.mapped('id'))]
    fecha_ini=fields.Date(string="Desde")
    fecha_fin=fields.Date(string="Hasta")
    analityc_account_ids=fields.Many2many('account.analytic.account',string="centro de costo")
    company_ids=fields.Many2many('res.company',string="Compañias",domain=company_domains)



    def print(self):
        for rec in self:
            return self.env.ref('eu_product_template_token.action_report_minum_stock_moves').report_action(self)


    def get_domain(self,key=False):
        for rec in self:
            domain=[]
            if len(rec.company_ids)>0:
                domain.append(('company_id','in',rec.company_ids.mapped('id')))
# verificamos fechas
            if rec.fecha_ini and key:
                domain.append(('date','>=',rec.fecha_ini))
            
            if rec.fecha_fin and key:
                domain.append(('date','<=',rec.fecha_fin))
            elif key :
                domain.append(('date','<=',TODAY))

# verificamos centros de costo
            if len(rec.analityc_account_ids)>0:
                domain.append(('analytic_account_id','in',rec.analityc_account_ids))

            return domain