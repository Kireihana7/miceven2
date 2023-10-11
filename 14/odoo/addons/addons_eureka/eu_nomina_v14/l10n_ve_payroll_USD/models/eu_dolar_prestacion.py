# -*- coding: utf-8 -*-

from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from math import floor
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, timedelta,date
from calendar import monthrange
from odoo.addons.l10n_ve_payroll.models.test import scrap_from_BCV_Prestaciones

TODAY=datetime.today()

class HrEmployeeEu(models.Model):
    _inherit = 'hr.employee'


    def create_prestacion(self):
        employees=self.env['hr.employee'].search([('fecha_inicio','!=',False)]).filtered(lambda x:  int(date.today().strftime("%d"))-1 <= int(x.fecha_inicio.strftime("%d")) <= int(date.today().strftime("%d"))+1)
        prestaciones=self.env['hr.prestaciones.employee.line'].search([('line_type','=','prestacion')]).filtered(lambda x:x.fecha.strftime("%m%Y") == date.today().strftime("%m%Y")) 
        for e in employees:
            rate_today=e.company_id.currency_id.parent_id.rate if e.company_id.currency_id.parent_id.rate >0 else 1
            exist_prestacion=prestaciones.filtered(lambda x: x.parent_id.id==e.id)
            if not exist_prestacion:
                line=[]
                if  e.company_id.journal_for_prestaciones:
                    apunte=self.env['account.move'].sudo().create({
                    'date':date.today(),
                    'journal_id':e.company_id.journal_for_prestaciones.id
                    })
                
                    #obtenemos el total cobrado en ese periodo
                    nominas=self.env['hr.payslip'].search([('is_anihilation','=',False),('employee_id','=',e.id)]).filtered(lambda x:x.date_to.month==date.today().month)
                    total=sum(x.total  for x in nominas.mapped("line_ids").filtered(lambda x: x.category_id.code=="BASIC"))
                    contrato=e.contract_id #obtenido contrato
                    sal_mensual=total #obtenido sal_mensual
                    sal_diario=sal_mensual/30 #obtenido sal_diario
                    ali_utilidades=(sal_diario*self.env.company.cant_dias_utilidades)/360 #obtenido utilidades 
                    dias_vacaciones=self.env.company.dias_vac_base + e.dias_bono
                    ali_vacaciones=(sal_diario*dias_vacaciones)/360 #obtenido vacaciones
                    antiguedad_adicional=0
                    try:
                            tasa_prestaciones=float(scrap_from_BCV_Prestaciones(self).replace(',','.')) #obtenido tasa
                    except:
                            tasa_prestaciones=1

                    #igualamos la antiguedad a 15 cuando estamos en el 3er mes
                    prestaciones_lines=self.env["hr.prestaciones.employee.line"].search([('line_type','=','prestacion'),('antiguedad','=',0),('parent_id','=',e.id),('company_id','=',e.company_id.id)])
                    #Si no es el tercer mes entonces iguala a 0
                    if (len(prestaciones_lines)+1)%3!=0:
                        antiguedad=0
                        antiguedad_adicional=0

                    else: #Sino entonces tiene un valor, esos 15 dias pueden variar toca estipular eso
                        antiguedad=15
                        if e.ano_antig>=2:
                            antiguedad_adicional=(e.ano_antig-1)*2
                    
                    antiguedad80=antiguedad+antiguedad_adicional #y listo tenemos las antiguedades
                    sal_dia_total=sal_diario+ali_vacaciones+ali_utilidades #tenemos diario total
                    prestaciones_mes=sal_dia_total*antiguedad80 #prestaciones del mes
                    #buscamos la linea anterior
                    linea_anterior=self.env['hr.prestaciones.employee.line'].search([('parent_id','=',e.id)],limit=1,order="id desc")
                    prestaciones_acumuladas=prestaciones_mes+(linea_anterior.prestaciones_acu if linea_anterior else 0) #prestaciones acumuladas
                    intereses=(prestaciones_acumuladas*tasa_prestaciones)/(100*12) #intereses obtenido
                    intereses_acum=intereses +(linea_anterior.intereses_acum if linea_anterior else 0)
                    presta_e_inte=prestaciones_mes+intereses+(linea_anterior.presta_e_inte if linea_anterior else 0) #presta e inte obtenido
                    day=e.fecha_inicio.day
                    max_day=monthrange(date.today().year,date.today().month)[1]
                    theday= max_day if max_day<=day else day
                    self.env['hr.prestaciones.employee.line'].create({
                        'line_type':'prestacion',
                        'parent_id': e.id,
                        'company_id':e.company_id.id, 
                        'fecha':date(date.today().year,date.today().month,theday) ,
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
                    })
                    if e.company_id.journal_for_prestaciones:
                        if intereses>0:
                            line.append({
                                'account_id':e.company_id.asiento_interes_pres.id,
                                'name': f"intereses {date.today()} - {e.name}",
                            'debit':intereses/rate_today,
                                'move_id':apunte.id
                            })
                            line.append({
                                'account_id':e.company_id.asiento_interes_paga.id,
                                'name': f"intereses {date.today()} - {e.name}",
                            'credit':intereses/rate_today,
                                'move_id':apunte.id
                            })
                        if prestaciones_mes>0:
                            line.append({
                                'account_id':e.company_id.asiento_prestaciones.id,
                                'name': f"Prestación {date.today()} - {e.name}",
                            'debit':prestaciones_mes/rate_today,
                                'move_id':apunte.id
                            })
                            line.append({
                                'account_id':e.company_id.asiento_antiguedad_p.id,
                                'name': f"Prestación {date.today()} - {e.name}",
                            'credit':prestaciones_mes/rate_today,
                                'move_id':apunte.id
                            })

                    
                if e.company_id.journal_for_prestaciones:
                    for li in line:
                        apunte.line_ids+=self.env['account.move.line'].create(li)




class HRPrestaciones(models.Model):
    _inherit = 'hr.prestaciones'
    def di_calculations(self):
        for rec in self:
            # recorremos nuestra linea de empleados
            """requiero obtener: 
            -contrato_actual -
            -sal_mensual -
            -salario basico(todas las asignaciones menos los bonos)-
            -sal_diario -
            -antiguedad-
            -antiguedad_adicional-
            -utilidades-
            -vacaciones-
            -antiguedad80-
            -total_diario-
            -prestaciones_mes-
            -anticipos_otorga
            -prestaciones_acu -
            -tasa_activa-
            -intereses -
            -preta_e_inte
            14/16"""

            line=[]
            if  rec.env.company.journal_for_prestaciones:
                apunte=rec.env['account.move'].sudo().create({
                'date':rec.fecha,
                'journal_id':rec.env.company.journal_for_prestaciones.id,
                'currency_id': rec.company_id.currency_id.parent_id.id,
                'manual_currency_exchange_rate':rec.company_id.currency_id.parent_id.rate
                })
            rate_today=rec.company_id.currency_id.parent_id.rate if rec.company_id.currency_id.parent_id.rate >0 else 1
            for empleado in rec.employee_id:
                #obtenemos el total cobrado en ese periodo
                nominas=self.env['hr.payslip'].search([('is_anihilation','=',False),('employee_id','=',empleado.id)]).filtered(lambda x:x.date_to.month==rec.fecha.month)
                total=sum(x.total  for x in nominas.mapped("line_ids").filtered(lambda x: x.category_id.code=="BASIC"))
                contrato=empleado.contract_id #obtenido contrato
                sal_mensual=total #obtenido sal_mensual
                sal_diario=sal_mensual/30 #obtenido sal_diario
                ali_utilidades=(sal_diario*rec.env.company.cant_dias_utilidades)/360 #obtenido utilidades 
                dias_vacaciones=rec.env.company.dias_vac_base + empleado.dias_bono
                ali_vacaciones=(sal_diario*dias_vacaciones)/360 #obtenido vacaciones
                antiguedad_adicional=0
                if not rec.check_manual:
                    try:
                        tasa_prestaciones=float(scrap_from_BCV_Prestaciones(self).replace(',','.')) #obtenido tasa
                    except:
                        raise UserError('Fallo en conexion con el banco intente de forma manual')
                else:
                    tasa_prestaciones=rec.tasa_prestaciones
                #igualamos la antiguedad a 15 cuando estamos en el 3er mes
                prestaciones_lines=self.env["hr.prestaciones.employee.line"].search([('line_type','=','prestacion'),('antiguedad','=',0),('parent_id','=',empleado.id),('company_id','=',empleado.company_id.id)])                #Si no es el tercer mes entonces iguala a 0
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
                            'debit':round(intereses/rate_today,4),
                            'move_id':apunte.id,
                            'amount_currency':round(intereses,4),
                            'currency_id': rec.company_id.currency_id.parent_id.id

                        })
                        line.append({
                            'account_id':rec.env.company.asiento_interes_paga.id,
                            'name': f"intereses {rec.fecha} - {empleado.name}",
                            'credit':round(intereses/rate_today,4),
                            'move_id':apunte.id,
                            'amount_currency':round(-1*intereses,4),
                            'currency_id': rec.company_id.currency_id.parent_id.id

                        })
                    if prestaciones_mes>0:
                        line.append({
                            'account_id':rec.env.company.asiento_prestaciones.id,
                            'name': f"Prestación {rec.fecha} - {empleado.name}",
                            'debit':round(prestaciones_mes/rate_today,4),
                            'move_id':apunte.id,
                            'amount_currency':round(prestaciones_mes,4),
                            'currency_id': rec.company_id.currency_id.parent_id.id

                        })
                        line.append({
                            'account_id':rec.env.company.asiento_antiguedad_p.id,
                            'name': f"Prestación {rec.fecha} - {empleado.name}",
                            'credit':round(prestaciones_mes/rate_today,4),
                            'move_id':apunte.id,
                            'amount_currency':round(-1*prestaciones_mes,4),
                            'currency_id': rec.company_id.currency_id.parent_id.id

                        })
            if rec.env.company.journal_for_prestaciones:
                for li in line:
                    apunte.line_ids+=rec.env['account.move.line'].create(li)
            rec.state="posted"

class HRAnticipos(models.Model):
    _inherit = 'hr.anticipos'
    
    def di_calculations(self):
        for rec in self:       
            # recorremos nuestra linea de empleados
            line=[]
            if  rec.env.company.journal_for_prestaciones:
                apunte=rec.env['account.move'].sudo().create({
                'date':rec.fecha,
                'journal_id':rec.env.company.journal_for_prestaciones.id,
                'currency_id': rec.company_id.currency_id.parent_id.id,
                'manual_currency_exchange_rate':rec.company_id.currency_id.parent_id.rate,
                'apply_manual_currency_exchange':True,
                })
            rate_today=rec.company_id.currency_id.parent_id.rate if rec.company_id.currency_id.parent_id.rate >0 else 1

            for empleado in rec.employee_id:
                #obtenemos el total cobrado en ese periodo


                #igualamos la antiguedad a 15 cuando estamos en el 3er mes
                prestaciones_lines=rec.env["hr.prestaciones.employee.line"].search([('parent_id','=',empleado.id),('company_id','=',empleado.company_id.id)])
                #Si no es el tercer mes entonces iguala a 0
                # if len(prestaciones_lines)<3:
                #     raise ValidationError(f"El empleado {empleado.name} no presenta prestaciones suficientes para generar anticipo, eliminelo de la lista")
                contrato=empleado.contract_id #obtenido contrato
                if not rec.anticipo_intereses:
                    if prestaciones_lines.filtered(lambda x: x.line_type=='anticipos' and x.fecha.year==rec.fecha.year):
                        raise UserError(f"El empleado {empleado.name} no puede solicitar otro anticipo por el año {rec.fecha.year}")
                    if prestaciones_lines[-1].prestaciones_acu<=0:
                        raise UserError("No puede generar un anticipo sin prestaciones acumuladas")
                        
                    else:
                        # previous=prestaciones_lines[-2]
                        anticipo=floor(prestaciones_lines[-1].prestaciones_acu*0.75)

                    rec.env['hr.prestaciones.employee.line'].create({
                        'line_type':'anticipo',
                        'parent_id': empleado.id,
                        'company_id':rec.env.company.id,
                        'fecha':rec.fecha,
                        'contract_id':contrato.id,
                        'porcentaje':rec.porcentaje,
                        'anticipos_otorga':anticipo, #falta
                        'prestaciones_acu':prestaciones_lines[-1].prestaciones_acu-anticipo,
                        'presta_e_inte':prestaciones_lines[-1].presta_e_inte-anticipo,
                        'parent_lote_anticip':self.id
                    })
                    if rec.env.company.journal_for_prestaciones:
                            if anticipo>0:
                                anticipo_usd = anticipo / rate_today
                                line.append({
                                    'account_id':rec.env.company.asiento_anticipo.id,
                                    'name': f"Anticipo {rec.fecha} - {empleado.name}",
                                    'debit':anticipo_usd,
                                    'amount_currency':round(anticipo,4),
                                    'move_id':apunte.id,
                                    'currency_id': rec.company_id.currency_id.parent_id.id,
                                    'manual_currency_exchange_rate':rec.company_id.currency_id.parent_id.rate,
                                })
                                line.append({
                                    'account_id':rec.env.company.asiento_antiguedad_anti_p.id,
                                    'name': f"Anticipo {rec.fecha} - {empleado.name}",
                                    'credit':anticipo_usd,
                                    'amount_currency':round(anticipo*-1,4),
                                    'move_id':apunte.id,
                                    'currency_id': rec.company_id.currency_id.parent_id.id,
                                    'manual_currency_exchange_rate':rec.company_id.currency_id.parent_id.rate,
                                })
                else:
                    if prestaciones_lines.filtered(lambda x: x.line_type=='anticipos' and x.fecha.year==rec.fecha.year and x.is_anticipo_intereses):
                        raise UserError(f"El empleado {empleado.name} no puede solicitar otro anticipo de intereses por el año {rec.fecha.year}")
                    if prestaciones_lines[-1].intereses_acum<=0:
                        raise UserError("No puede generar un anticipo de intereses sin intereses acumulados")
                        
                    else:
                        previous=prestaciones_lines[-2]
                        last=prestaciones_lines[-1]
                        anticipo=prestaciones_lines[-1].intereses_acum

                    rec.env['hr.prestaciones.employee.line'].create({
                        'line_type':'anticipo',
                        'parent_id': empleado.id,
                        'company_id':rec.env.company.id,
                        'fecha':rec.fecha,
                        'contract_id':contrato.id,
                        'porcentaje':100,
                        'anticipos_otorga':anticipo,
                        'intereses_acum':0,
                        'prestaciones_acu':last.prestaciones_acu,
                        'presta_e_inte':last.presta_e_inte-anticipo,
                        'parent_lote_anticip':self.id
                    })
                    if rec.env.company.journal_for_prestaciones:
                            if anticipo>0:
                                line.append({
                                    'account_id':rec.env.company.asiento_interes_anti.id,
                                    'name': f"Anticipo Int. {rec.fecha} - {empleado.name}",
                                    'debit':round(anticipo/rate_today,4),
                                    'amount_currency':round(anticipo,4),
                                    'move_id':apunte.id,
                                    'currency_id': self.company_id.currency_id.parent_id.id,
                                    'manual_currency_exchange_rate':rec.company_id.currency_id.parent_id.rate,

                                })
                                line.append({
                                    'account_id':rec.env.company.asiento_interes_anti_paga.id,
                                    'name': f"Anticipo Int. {rec.fecha} - {empleado.name}",
                                    'credit':round(-1*anticipo/rate_today,4),
                                    'move_id':apunte.id,
                                    'currency_id': self.company_id.currency_id.parent_id.id,
                                    'amount_currency':round(anticipo,4),
                                    'manual_currency_exchange_rate':rec.company_id.currency_id.parent_id.rate,
                                })
            if rec.env.company.journal_for_prestaciones:    
                    for li in line:
                        apunte.line_ids+=rec.env['account.move.line'].create(li)
                
            rec.state="posted"



class HrPrestacionLines(models.Model):
    _inherit = "hr.prestaciones.employee.line"


    currency_rate_date=fields.Float(store=True,string="Tasa del Día",compute="_compute_tasa")
    prestaciones_mes_ref= fields.Float(store=True,string="ref. Prestación mes",compute="_compute_ref" )
    anticipos_otorga_ref= fields.Float (store=True,string="ref. Anticipo otorgado",compute="_compute_ref" )
    prestaciones_acu_ref= fields.Float(store=True,string="ref. Prest. Acum.",compute="_compute_ref" )
    intereses_ref= fields.Float(store=True,string="ref. intereses",compute="_compute_ref" )
    intereses_acum_ref= fields.Float(store=True,string="ref. intereses acum.",compute="_compute_ref" )
    presta_e_inte_ref= fields.Float(store=True,string="ref. prest. e int. acum",compute="_compute_ref" )

    @api.depends('company_id')
    def _compute_tasa(self):
        for rec in self:
            rec.currency_rate_date=rec.company_id.currency_id.parent_id.rate


    @api.depends('prestaciones_mes','anticipos_otorga','porcentaje','prestaciones_acu','intereses','intereses_acum','presta_e_inte')
    def _compute_ref(self):
        for rec in self:
            rec.prestaciones_mes_ref=round(rec.prestaciones_mes/rec.currency_rate_date,4) if rec.currency_rate_date>0 else 0
            rec.anticipos_otorga_ref=round(rec.anticipos_otorga/rec.currency_rate_date,4) if rec.currency_rate_date>0 else 0
            rec.prestaciones_acu_ref=round(rec.prestaciones_acu/rec.currency_rate_date,4) if rec.currency_rate_date>0 else 0
            rec.intereses_ref=round(rec.intereses/rec.currency_rate_date,4) if rec.currency_rate_date>0 else 0
            rec.intereses_acum_ref=round(rec.intereses_acum/rec.currency_rate_date,4) if rec.currency_rate_date>0 else 0
            rec.presta_e_inte_ref=round(rec.presta_e_inte/rec.currency_rate_date,4) if rec.currency_rate_date>0 else 0
    
