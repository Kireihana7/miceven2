# -*- coding: utf-8 -*-
from math import floor
from odoo.exceptions import UserError,ValidationError
from odoo import models, fields,api
from datetime import datetime, timedelta,date
from calendar import monthrange
from openerp.addons.l10n_ve_payroll.models.test import  scrap_from_BCV_Prestaciones
TODAY=date.today()
class HRPrestaciones(models.Model):
    _inherit = 'hr.prestaciones'
    def _get_nominas(self,empleado):
            return self.env['hr.payslip'].search([('corporate_type','=',False),('is_anihilation','=',False),('employee_id','=',empleado.id)]).filtered(lambda x:x.date_to.month==self.fecha.month)
class HRPrestacionesCorporate(models.Model):
    _name = 'hr.prestaciones.corporate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    its_super_secret=fields.Boolean(string="Shh", groups="eu_payslip_corporate_view.corporate_super_payslip_group")
    name=fields.Char(default=f"Prestaciones {TODAY.strftime('%B de %Y')}",tracking=True)
    employee_id=fields.Many2many('hr.employee',string="Empleados", domain=[('contract_id.state','in',['open','draft'])],tracking=True)
    fecha=fields.Date(default=date(TODAY.year,TODAY.month,monthrange(TODAY.year, TODAY.month)[1]),tracking=True)
    department_id=fields.Many2one('hr.department', "Departamento",tracking=True)
    cargo_id=fields.Many2one('hr.job',"Cargo",tracking=True)
    category_id_filter=fields.Many2one('hr.employee.category',string="Categoria Empleado",tracking=True)
    company_id=fields.Many2one("res.company",default=lambda self: self.env.company,tracking=True)
    check_manual=fields.Boolean("Utilizar Tasa Manual",tracking=True)
    tasa_prestaciones=fields.Float("Tasa de prestación",tracking=True)
    state=fields.Selection([('draft','Borrador'),('posted','Publicado')],default="draft",tracking=True)

    def _get_nominas(self,empleado):
            return self.env['hr.payslip'].search([('corporate_type','=',True),('is_anihilation','=',False),('employee_id','=',empleado.id)]).filtered(lambda x:x.date_to.month==self.fecha.month)

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
            if  rec.env.company.journal_for_prestaciones_corporate:
                apunte=rec.env['account.move'].sudo().create({
                'date':rec.fecha,
                'journal_id':rec.env.company.journal_for_prestaciones_corporate.id
                })
            
            for empleado in rec.employee_id:
                #obtenemos el total cobrado en ese periodo
                nominas=rec._get_nominas(empleado)
                total=sum(x.total  for x in nominas.mapped("line_ids").filtered(lambda x: x.category_id.code=="Bono"))
                contrato=empleado.contract_id #obtenido contrato
                sal_mensual=total #obtenido sal_mensual
                sal_diario=sal_mensual/30 #obtenido sal_diario
                # ali_utilidades=(sal_diario*rec.env.company.cant_dias_utilidades)/360 #obtenido utilidades 
                # dias_vacaciones=rec.env.company.dias_vac_base + empleado.dias_bono
                # ali_vacaciones=(sal_diario*dias_vacaciones)/360 #obtenido vacaciones
                antiguedad_adicional=0
                if not rec.check_manual:
                    try:
                        tasa_prestaciones=float(scrap_from_BCV_Prestaciones(self).replace(',','.')) #obtenido tasa
                    except:
                        raise UserError('Fallo en conexion con el banco')
                else:
                    tasa_prestaciones=rec.tasa_prestaciones
                #igualamos la antiguedad a 15 cuando estamos en el 3er mes
                prestaciones_lines=rec.env["hr.prestaciones.corporate.employee.line"].search([('parent_id','=',empleado.id),('company_id','=',empleado.company_id.id)])
                #Si no es el tercer mes entonces iguala a 0
                if (len(prestaciones_lines)+1)%3!=0:
                    antiguedad=0
                    antiguedad_adicional=0

                else: #Sino entonces tiene un valor, esos 15 dias pueden variar toca estipular eso
                    antiguedad=15
                    if empleado.ano_antig>=2:
                        antiguedad_adicional=(empleado.ano_antig-1)*2
                
                antiguedad80=antiguedad+antiguedad_adicional #y listo tenemos las antiguedades
                sal_dia_total=sal_diario #+ali_vacaciones+ali_utilidades tenemos diario total
                prestaciones_mes=sal_dia_total*antiguedad80 #prestaciones del mes
                #buscamos la linea anterior
                linea_anterior=self.env['hr.prestaciones.corporate.employee.line'].search([('parent_id','=',empleado.id)],limit=1,order="id desc")
                prestaciones_acumuladas=prestaciones_mes+(linea_anterior.prestaciones_acu if linea_anterior else 0) #prestaciones acumuladas
                intereses=(prestaciones_acumuladas*tasa_prestaciones)/(100*12) #intereses obtenido
                intereses_acum=intereses +(linea_anterior.intereses_acum if linea_anterior else 0)
                presta_e_inte=prestaciones_mes+intereses+(linea_anterior.presta_e_inte if linea_anterior else 0) #presta e inte obtenido
                rec.env['hr.prestaciones.corporate.employee.line'].create({
                    'line_type':'prestacion',
                    'parent_id': empleado.id,
                    'company_id':rec.env.company.id,
                    'fecha':rec.fecha,
                    'contract_id':contrato.id,
                    'sal_mensual':sal_mensual,
                    'sal_diario':sal_diario,
                    'antiguedad':antiguedad,
                    'antiguedad_adicional':antiguedad_adicional,
                    'antiguedad80':antiguedad80,
                    'total_diario':sal_dia_total,
                    'prestaciones_mes':prestaciones_mes,
                    'anticipos_otorga':False, #falta
                    'prestaciones_acu':prestaciones_acumuladas,
                    'tasa_activa':tasa_prestaciones,
                    'intereses':intereses,
                    'intereses_acum':intereses_acum,
                    'presta_e_inte':presta_e_inte,
                    'parent_lote_prest':rec.id
                })
                if rec.env.company.journal_for_prestaciones_corporate:
                    if intereses>0:
                        line.append({
                            'account_id':rec.env.company.asiento_interes_pres_corporate.id,
                            'name': f"intereses {rec.fecha} - {empleado.name}",
                            'debit':intereses,
                            'move_id':apunte.id
                        })
                        line.append({
                            'account_id':rec.env.company.asiento_interes_paga_corporate.id,
                            'name': f"intereses {rec.fecha} - {empleado.name}",
                            'credit':intereses,
                            'move_id':apunte.id
                        })
                    if prestaciones_mes>0:
                        line.append({
                            'account_id':rec.env.company.asiento_prestaciones_corporate.id,
                            'name': f"Prestación {rec.fecha} - {empleado.name}",
                            'debit':prestaciones_mes,
                            'move_id':apunte.id
                        })
                        line.append({
                            'account_id':rec.env.company.asiento_antiguedad_p_corporate.id,
                            'name': f"Prestación {rec.fecha} - {empleado.name}",
                            'credit':prestaciones_mes,
                            'move_id':apunte.id
                        })
            if rec.env.company.journal_for_prestaciones_corporate:
                for li in line:
                    apunte.line_ids+=rec.env['account.move.line'].create(li)
            rec.state="posted"
                
                

            
    @api.onchange('department_id','cargo_id','category_id_filter')
    def onchange_filters(self):
        for rec in self:
            domain=[]
            if rec.category_id_filter:
                domain.append(('category_ids','=',rec.category_id_filter.id))
            if rec.department_id:
                domain.append(('department_id','=',rec.department_id.id))
            if rec.cargo_id:
                domain.append(('contract_id.job_id','=',rec.cargo_id.id))

            empleados=False
            if len(domain)>0:
                empleados=self.env['hr.employee'].search(domain)
            if empleados:
                rec.employee_id=empleados


    # @api.onchange('cargo_id')
    # def onchange_cargo(self):
    #     for rec in self:
    #         empleados=self.env['hr.employee'].search([('contract_id.job_id','=',rec.cargo_id.id)])
    #         rec.employee_id=empleados




class HRAnticiposCorporate(models.Model):
    _name = 'hr.anticipos.corporate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    its_super_secret=fields.Boolean(string="Shh", groups="eu_payslip_corporate_view.corporate_super_payslip_group")
    name=fields.Char(default=f"Anticipos de Prestaciones",tracking=True)
    employee_id=fields.Many2many('hr.employee',relation='employee_anticipo_corporate',column1="empleado",column2="anticipo",string="Empleados", domain=['|',('mes_antig','>',3),('ano_antig','>',0)],tracking=True)
    fecha=fields.Date(default=date(TODAY.year,TODAY.month,monthrange(TODAY.year, TODAY.month)[1]),tracking=True)
    department_id=fields.Many2one('hr.department', "Departamento",tracking=True)
    cargo_id=fields.Many2one('hr.job',"Cargo",tracking=True)
    account_move_id=fields.Many2one('account.move',string="apunte contable",tracking=True)
    category_id_filter=fields.Many2one('hr.employee.category',string="Categoria Empleado",tracking=True)
    company_id=fields.Many2one("res.company",default=lambda self: self.env.company,tracking=True)
    porcentaje=fields.Float("Porcentaje de los anticipos",tracking=True,default=75)
    state=fields.Selection([('draft','Borrador'),('posted','Publicado')],default="draft",tracking=True)
    anticipo_intereses=fields.Boolean(string="¿Es un anticipo de Intereses?",tracking=True)
    @api.onchange('department_id','cargo_id','category_id_filter')
    def onchange_filters(self):
        for rec in self:
            domain=[]
            if rec.category_id_filter:
                domain.append(('category_ids','=',rec.category_id_filter.id))
            if rec.department_id:
                domain.append(('department_id','=',rec.department_id.id))
            if rec.cargo_id:
                domain.append(('contract_id.job_id','=',rec.cargo_id.id))

            empleados=False
            if len(domain)>0:
                empleados=self.env['hr.employee'].search(domain)
            if empleados:
                rec.employee_id=empleados


    def di_calculations(self):
        for rec in self:       
            # recorremos nuestra linea de empleados
            line=[]
            if  rec.env.company.journal_for_prestaciones_corporate:
                apunte=rec.env['account.move'].sudo().create({
                'date':rec.fecha,
                'journal_id':rec.env.company.journal_for_prestaciones_corporate.id
                })
            
            for empleado in rec.employee_id:
                #obtenemos el total cobrado en ese periodo


                #igualamos la antiguedad a 15 cuando estamos en el 3er mes
                prestaciones_lines=rec.env["hr.prestaciones.corporate.employee.line"].search([('parent_id','=',empleado.id),('company_id','=',empleado.company_id.id)])
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

                    rec.env['hr.prestaciones.corporate.employee.line'].create({
                        'line_type':'anticipo',
                        'parent_id': empleado.id,
                        'company_id':rec.env.company.id,
                        'fecha':rec.fecha,
                        'contract_id':contrato.id,
                        'porcentaje':rec.porcentaje,
                        'anticipos_otorga':anticipo, #falta
                        'prestaciones_acu':prestaciones_lines[-1].prestaciones_acu-anticipo,
                        'presta_e_inte':prestaciones_lines[-1].presta_e_inte-anticipo,
                        'parent_lote_anticip':rec.id
                    })
                    if rec.env.company.journal_for_prestaciones_corporate:
                            if anticipo>0:
                                line.append({
                                    'account_id':rec.env.company.asiento_anticipo_corporate.id,
                                    'name': f"Anticipo {rec.fecha} - {empleado.name}",
                                    'debit':anticipo,
                                    'move_id':apunte.id
                                })
                                line.append({
                                    'account_id':rec.env.company.asiento_antiguedad_anti_p_corporate.id,
                                    'name': f"Anticipo {rec.fecha} - {empleado.name}",
                                    'credit':anticipo,
                                    'move_id':apunte.id
                                })
                else:
                    if prestaciones_lines.filtered(lambda x: x.line_type=='anticipos' and x.fecha.year==rec.fecha.year and x.is_anticipo_intereses):
                        raise UserError(f"El empleado {empleado.name} no puede solicitar otro anticipo de intereses por el año {rec.fecha.year}")
                    if prestaciones_lines[-1].intereses_acum<=0:
                        raise UserError("No puede generar un anticipo de intereses sin intereses acumulados")
                        
                    else:
                        # previous=prestaciones_lines[-2]
                        last=prestaciones_lines[-1]
                        anticipo=prestaciones_lines[-1].intereses_acum

                    rec.env['hr.prestaciones.corporate.employee.line'].create({
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
                        'parent_lote_anticip':rec.id
                    })
                    if rec.env.company.journal_for_prestaciones_corporate:
                            if anticipo>0:
                                line.append({
                                    'account_id':rec.env.company.asiento_interes_anti_corporate.id,
                                    'name': f"Anticipo Int. {rec.fecha} - {empleado.name}",
                                    'debit':anticipo,
                                    'move_id':apunte.id
                                })
                                line.append({
                                    'account_id':rec.env.company.asiento_interes_anti_paga_corporate.id,
                                    'name': f"Anticipo Int. {rec.fecha} - {empleado.name}",
                                    'credit':anticipo,
                                    'move_id':apunte.id
                                })
            if rec.env.company.journal_for_prestaciones_corporate:    
                    for li in line:
                        apunte.line_ids+=rec.env['account.move.line'].create(li)
                
            rec.state="posted"

    def get_anticipo_per_employee(self,employee_id):
        for rec in self:
            return rec.env["hr.prestaciones.corporate.employee.line"].search([('line_type','=','anticipo'),('parent_id','=',employee_id.id),('parent_lote_anticip','=',rec.id)])

        