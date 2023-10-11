# -*- coding: utf-8 -*-

from math import floor
from odoo.exceptions import UserError,ValidationError
from odoo import models, fields,api
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta,date
from calendar import monthrange
class EuHrLiquidation(models.Model):
    _inherit="hr.liquidacion"
    
    

    @api.depends("employee_id","company_id","total_vacciones","vacaciones_disfrutadas","ao","mes")
    def _get_dias_vacaciones_utili(self):
        for rec in self:
            dias_vaca=0
            tomadas=len(rec.vacaciones_disfrutadas)
            restantes=rec.total_vacciones-tomadas
            if rec.mes>=1:
                restantes+=1
            rec.vacaciones_restantes=restantes
            if rec.ao>=2 :
                for i in range(1,restantes+1):
                    aux=rec.company_id.dias_vac_base + rec.employee_id.dias_bono-i
                    if rec.employee_id.contract_id.parent_collect_contract_id and  rec.employee_id.contract_id.parent_collect_contract_id.additional_days_bonification:
                        aux+=rec.employee_id.contract_id.parent_collect_contract_id.additional_days_bonification
                    dias_vaca+=aux if aux>=15 else 15
            else:
                dias_vaca=15*restantes
            dias_vaca+= ((15/12)*rec.mes if rec.mes else 0 )

            rec.days_of_vacations=dias_vaca
            ultima_utility=rec.env["hr.payslip"].search([('employee_id','=',rec.employee_id.id),('is_utility','=',True),('state','not in',['cancel','draft'])],limit=1,order="date_to desc")
            if ultima_utility:

                time_since_last_u=(rec.fecha-ultima_utility.date_to).days
            else:
                time_since_last_u=rec.ao*360+rec.mes*30+rec.dia
            
            rec.days_of_utilidades=(rec.company_id.cant_dias_utilidades/360)*(time_since_last_u)
            rec.total_utilidades=rec.days_of_utilidades*rec.sal_diario

    @api.depends("employee_id","fecha")
    def _get_sal_diario(self):
        for rec in self:
                nominas=rec.env['hr.payslip'].search([('is_anihilation','=',False),('employee_id','=',rec.employee_id.id)]).filtered(lambda x:x.date_to.month==rec.fecha.month)
                total=sum(x.total  for x in nominas.mapped("line_ids").filtered(lambda x: x.category_id.code=="BASIC"))
                contrato=rec.employee_id.contract_id #obtenido contrato
                sal_mensual=total #obtenido sal_mensual
                sal_diario=sal_mensual/30 #obtenido sal_diario
                rec.alicuota_utilidades=(sal_diario*rec.env.company.cant_dias_utilidades)/360 #obtenido utilidades 
                if rec.employee_id.contract_id.parent_collect_contract_id:
                    dias_vacaciones=rec.env.company.dias_vac_base + rec.employee_id.dias_bono +rec.employee_id.contract_id.parent_collect_contract_id.additional_days_bonification
                else:
                    dias_vacaciones=rec.env.company.dias_vac_base + rec.employee_id.dias_bono
                rec.alicuota_vacaciones=(sal_diario*dias_vacaciones)/360 #obtenido vacaciones
                sal_dia_total=sal_diario+rec.alicuota_vacaciones+rec.alicuota_utilidades #tenemos diario integral
                if sal_dia_total<1:
                    rec.sal_diario=rec.contract_id.wage/30
                else:
                    rec.sal_diario=sal_dia_total