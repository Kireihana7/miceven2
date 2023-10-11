# -*- coding: utf-8 -*-

from math import floor
from odoo.exceptions import UserError,ValidationError
from odoo import models, fields,api
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta,date
from calendar import monthrange
from odoo.addons.l10n_ve_payroll.models.test import scrap_from_BCV_Prestaciones

class HREuPrestaciones(models.Model):
    _inherit = 'hr.prestaciones'

    def di_calculations(self):
        for rec in self:

            line=[]
            if  rec.env.company.journal_for_prestaciones:
                apunte=rec.env['account.move'].sudo().create({
                'date':rec.fecha,
                'journal_id':rec.env.company.journal_for_prestaciones.id
                })
            for empleado in rec.employee_id:
                #obtenemos el total cobrado en ese periodo
                nominas=self.env['hr.payslip'].search([('is_anihilation','=',False),('employee_id','=',empleado.id)]).filtered(lambda x:x.date_to.month==rec.fecha.month)
                total=sum(x.total  for x in nominas.mapped("line_ids").filtered(lambda x: x.category_id.code=="BASIC"))
                contrato=empleado.contract_id #obtenido contrato
                sal_mensual=total #obtenido sal_mensual
                sal_diario=sal_mensual/30 #obtenido sal_diario
                ali_utilidades=(sal_diario*rec.env.company.cant_dias_utilidades)/360 #obtenido utilidades
                if rec.employee_id.contract_id.parent_collect_contract_id and  rec.employee_id.contract_id.parent_collect_contract_id.additional_days_bonification:
                    dias_vacaciones=rec.env.company.dias_vac_base + empleado.dias_bono + rec.employee_id.contract_id.parent_collect_contract_id.additional_days_bonification
                else:
                    dias_vacaciones=rec.env.company.dias_vac_base + empleado.dias_bono

                ali_vacaciones=(sal_diario*dias_vacaciones)/360 #obtenido vacaciones
                antiguedad_adicional=0
                try:
                    tasa_prestaciones=float(scrap_from_BCV_Prestaciones(self).replace(',','.')) #obtenido tasa
                except:
                    raise UserError(tasa_prestaciones)

                #igualamos la antiguedad a 15 cuando estamos en el 3er mes
                prestaciones_lines=rec.env["hr.prestaciones.employee.line"].search([('parent_id','=',empleado.id),('company_id','=',empleado.company_id.id)])
                #Si no es el tercer mes entonces iguala a 0
                if (len(prestaciones_lines)+1)%3!=0:
                    antiguedad=0
                    antiguedad_adicional=0

                else: #Sino entonces tiene un valor, esos 15 dias pueden variar toca estipular eso
                    antiguedad=15
                    if empleado.ano_antig>=2:
                        antiguedad_adicional=(empleado.ano_antig-1)*2
                
                antiguedad80=antiguedad+antiguedad_adicional #y listo tenemos las antiguedades
                sal_dia_total=sal_diario+ali_vacaciones+ali_utilidades #tenemos diario total
                prestaciones_mes=sal_dia_total*antiguedad80 #prestaciones del mes
                #buscamos la linea anterior
                linea_anterior=self.env['hr.prestaciones.employee.line'].search([('parent_id','=',empleado.id)],limit=1,order="id desc")
                prestaciones_acumuladas=prestaciones_mes+(linea_anterior.prestaciones_acu if linea_anterior else 0) #prestaciones acumuladas
                intereses=(prestaciones_acumuladas*tasa_prestaciones)/(100*12) #intereses obtenido
                intereses_acum=intereses +(linea_anterior.intereses_acum if linea_anterior else 0)
                presta_e_inte=prestaciones_mes+intereses+(linea_anterior.presta_e_inte if linea_anterior else 0) #presta e inte obtenido
                rec.env['hr.prestaciones.employee.line'].create({
                    'line_type':'prestacion',
                    'parent_id': empleado.id,
                    'company_id':rec.env.company.id,
                    'fecha':rec.fecha,
                    'contract_id':contrato.id,
                    'sal_mensual':sal_mensual,
                    'sal_diario':sal_diario,
                    'antiguedad':antiguedad,
                    'antiguedad_adicional':antiguedad_adicional,
                    'utilidades':ali_utilidades,
                    'vacaciones':ali_vacaciones,
                    'antiguedad80':antiguedad80,
                    'total_diario':sal_dia_total,
                    'prestaciones_mes':prestaciones_mes,
                    'anticipos_otorga':False, #falta
                    'prestaciones_acu':prestaciones_acumuladas,
                    'tasa_activa':tasa_prestaciones,
                    'intereses':intereses,
                    'intereses_acum':intereses_acum,
                    'presta_e_inte':presta_e_inte,
                    'parent_lote_prest':self.id
                })
                if rec.env.company.journal_for_prestaciones:
                    if intereses>0:
                        line.append({
                            'account_id':rec.env.company.asiento_interes_pres.id,
                            'name': f"intereses {rec.fecha} - {empleado.name}",
                            'debit':intereses,
                            'move_id':apunte.id
                        })
                        line.append({
                            'account_id':rec.env.company.asiento_interes_paga.id,
                            'name': f"intereses {rec.fecha} - {empleado.name}",
                            'credit':intereses,
                            'move_id':apunte.id
                        })
                    if prestaciones_mes>0:
                        line.append({
                            'account_id':rec.env.company.asiento_prestaciones.id,
                            'name': f"Prestación {rec.fecha} - {empleado.name}",
                            'debit':prestaciones_mes,
                            'move_id':apunte.id
                        })
                        line.append({
                            'account_id':rec.env.company.asiento_antiguedad_p.id,
                            'name': f"Prestación {rec.fecha} - {empleado.name}",
                            'credit':prestaciones_mes,
                            'move_id':apunte.id
                        })
            if rec.env.company.journal_for_prestaciones:
                for li in line:
                    apunte.line_ids+=rec.env['account.move.line'].create(li)
                