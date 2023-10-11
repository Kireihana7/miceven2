# -*- coding: utf-8 -*-

from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from calendar import monthrange,weekday
from odoo import models, fields,api

class EuHrPayslip(models.Model):
    _inherit="hr.payslip"
    
    

    @api.onchange('date_from','is_vacation','anno_vacaciones_designado')
    def _onchange_is_vacation(self,days_preset=0,colective=False):
        for rec in self:
            
            if rec.is_vacation and rec.employee_id:
                
                total=1
                contador=0
                date_to= rec.date_from
                counter_festivities=0
                if days_preset and colective:
                    dias_vacacionales=days_preset
                    date_fixed=date_to+relativedelta(days = days_preset)
                elif days_preset:
                    dias_vacacionales=days_preset
                else:
                    dias_vacacionales= rec.dias_vacaciones+rec.dias_bonificaciones
                    if rec.employee_id.contract_id.parent_collect_contract_id and  rec.employee_id.contract_id.parent_collect_contract_id.additional_days_bonification:
                        dias_vacacionales+=rec.employee_id.contract_id.parent_collect_contract_id.additional_days_bonification
                while total<dias_vacacionales:
                    if date_to in rec.last_calendario_feriado.holidays_lines_ids.mapped("fecha") and date_to.weekday() not in [5,6]:
                        counter_festivities+=1
                    elif date_to.weekday()  in [5,6]:
                        pass
                    else:
                        total+=1
                    date_to= date_to+relativedelta(days =1)
                if date_fixed:
                    rec.date_to = date_fixed
                else:
                    rec.date_to = date_to

                rec._calcular_lunes()
                counter_festivities+=contador
                rec.dias_feriados=rec.sabado_periodo+rec.domingo_periodo+counter_festivities