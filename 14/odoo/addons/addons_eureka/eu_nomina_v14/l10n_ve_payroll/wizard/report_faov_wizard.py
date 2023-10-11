# -*- coding: utf-8 -*-


from odoo import fields, models,api
from odoo.exceptions import UserError
from datetime import date,datetime
from calendar import monthrange,monthcalendar,setfirstweekday
TODAY = date.today()


class FaovReportWizard(models.TransientModel):
    _name = 'report.faov.wizard'
    _description = 'Reporte de Faov por distintos periodos'




    

    para_fecha = fields.Date("Fecha Inicio", default=TODAY)
    periodo = fields.Selection([('semanal','Semanal'),('quincenal','Quincenal'),('mensual','Mensual')],string="periodos de desglose")
    filtro=fields.Selection([('all', 'Sin filtrado'),
        ('with_contracts', 'Contratados'),
        # ('with_payslip_only', 'Con nómina pagada'),
    ],  default="with_contracts", string="Filtrar por")
    employee_tags=fields.Many2many('hr.employee.category',string="Categorias empleados")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company.id,invisible=True)

    
    def month_weeks(self,year,month):
        setfirstweekday(3)
        arraytoextirpate=monthcalendar(year,month)
        array=list(filter(lambda x: x[0]!=0,arraytoextirpate))
        y=1
        
        for i in  range(0,len(array[-1])):
            if array[-1][i]==0:
                array[-1][i]=y
                y+=1
        
        
        return array



    def abs_venezuelan_weeksit_range(self,array,dates):
        get_first_day=array[0][0]
        init_date=date(dates.year,dates.month,get_first_day)
        # confirmamos si la ultima semana pasa del mes
        if array[-1][0]>array[-1][-1]:
            last_date=date(dates.year,dates.month+1,array[-1][-1])
        else:
            last_date=date(dates.year,dates.month,array[-1][-1])
        week_separation=[]
        for i in array:
            week_separation.append([date(dates.year,dates.month,i[0]),date(dates.year,dates.month,i[-1])])
        week_separation[-1][-1]=last_date
        
        return week_separation


    def array_of_weeks_for_sumatory(self,array):
        obj_abacus={}
        for i in range(1,len(array)+1):
            obj_abacus[i]=0
        
        return obj_abacus

    def update_abacus(self,object,position,value):
        object[position]+=value
        
        return object
        
    def print_report(self):
        
        
        return self.env.ref('l10n_ve_payroll.action_report_faov_periodo').report_action(self)
        

# class ParticularReport(models.AbstractModel):
#     _name = 'report.l10n_ve_payroll.report_acum_rel_nomina_var'

#     def _get_report_values(self, docids, data=None):
#         # get the report action back as we will need its data
        
#         # return a custom rendering context
#         return {
#             'doc_ids':data.get("doc_ids"),
#             'doc_model': data.get("doc_model"),
#             'docs':self.env['hr.employee'].search([('id','in',data.get("doc_ids"))]),
#             'datas':data

#         }