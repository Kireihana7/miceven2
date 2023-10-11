# -*- coding: utf-8 -*-
#flagship----aqui cambiamos el calculo del emonto en ingles
from math import floor
from odoo.exceptions import UserError,ValidationError
from odoo import models, fields,api
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta,date
from calendar import monthrange
TODAY=date.today()

class HRLiquidacion(models.Model):
    _name = 'hr.liquidacion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = "Aca se cargan los modelos para las liquidaciones, ademas de producir el cambio de estado en el empleado"

    company_id=fields.Many2one("res.company",default=lambda self: self.env.company,tracking=True)
    name=fields.Char(default=f"Liquidaciones {TODAY.strftime('%B de %Y')}") #a cambiar a un onchange o una funcion on wrte
    employee_id=fields.Many2one('hr.employee',string="Empleado",tracking=True)
    fecha=fields.Date(default=date(TODAY.year,TODAY.month,monthrange(TODAY.year, TODAY.month)[1]),tracking=True)
    contract_id=fields.Many2one('hr.contract',related="employee_id.contract_id", store=True,string="Contrato actual",tracking=True)
    is_variable=fields.Boolean('Salario variable', compute="_compute_is_variable",tracking=True)
    lote_id=fields.Many2one("hr.liquidacion.lote",string="lote de liquidaciones")
    motivo=fields.Selection([('renuncia','Renuncia'),('retiro','Retiro'),('despido','Despido'),('otro','Otros motivos')],string="Motivo de Liquidación",tracking=True)
    observations=fields.Char(string="Observaciones",tracking=True)
    #datos del empleado
    ao=fields.Integer(compute="_compute_antig", store=True,string="Años de servicio",tracking=True)
    mes=fields.Integer(compute="_compute_antig", store=True,string="Meses",tracking=True)
    dia=fields.Integer(compute="_compute_antig", store=True,string="Dias",tracking=True)
    @api.depends('employee_id','fecha')
    def _compute_antig(self):
        for rec in self:
            rec.ao=relativedelta(rec.fecha, rec.employee_id.fecha_inicio).years 
            rec.mes= relativedelta(rec.fecha, rec.employee_id.fecha_inicio).months
            rec.dia= relativedelta(rec.fecha, rec.employee_id.fecha_inicio).days
            
    #listado de las vacaciones
    vacaciones_disfrutadas=fields.Many2many('hr.payslip',compute="_get_vacaciones_disfrutada", string="Vacaciones Disfrutadas")
    total_vacciones=fields.Integer(related="employee_id.vacaciones_total",string="Total de Vacaciones",tracking=True)
    vacaciones_restantes=fields.Integer()

    #Prestaciones
    Last_prestacion=fields.Many2one("hr.prestaciones.employee.line",compute="_get_last_prestacion_line",string="Ultima prestación",tracking=True)
    prestacion_total=fields.Float(related="Last_prestacion.prestaciones_acu", string="Prestaciones Lt. A y B",store=True)

    #Utilidades

    alicuota_utilidades=fields.Float(compute="_get_sal_diario",store=True)
    alicuota_vacaciones=fields.Float(compute="_get_sal_diario",store=True)
    sal_diario=fields.Float(compute="_get_sal_diario",string="salario diario Integral")
    minimo_a_liquidar=fields.Float(compute="_get_minimo_a_liquidar",string="Prestaciones sociales Lt. C")
    monto_art92_liq=fields.Float(compute="_comparate_liquidates",store=True,readonly=False,string="Art. 92")
    total_liquidar=fields.Float()
    adicionales=fields.Float(string="Adicionales")
    intereses_prestaciones=fields.Float(related="Last_prestacion.intereses_acum",store=True)
    days_of_vacations=fields.Integer(compute="_get_dias_vacaciones_utili",string="Dias de vacaciones",store=True)
    days_of_utilidades=fields.Float(compute="_get_dias_vacaciones_utili",string="Dias de utilidades",store=True)
    total_utilidades=fields.Float(string="Total Utilidades",store=True)
    total_vacaciones=fields.Integer(related="employee_id.vacaciones_total") #vacaciones_total
    vacaciones_por_pagar=fields.Many2many('hr.payslip',tracking=True)
    struct_vacaciones=fields.Many2one("hr.payroll.structure",default=lambda self: self.env.company.struct_vacaciones,tracking=True)
    struct_liqidation=fields.Many2one("hr.payroll.structure",default=lambda self: self.env.company.struct_liquidacion,tracking=True)
    great_sumatory=fields.Float("Total finiquitado",default=0,tracking=True)
    salario_promedio=fields.Float("Salario Prom. diario",store=True, compute="_compute_salario_promedio",tracking=True)
    liquidado=fields.Many2one('hr.prestaciones.employee.line',"linea de liquidación",tracking=True)
    terminated_payslip=fields.Many2one("hr.payslip","entrada de liquidación",tracking=True)
    vacation_payslip=fields.Many2one("hr.payslip","entrada de liquidación vacaciones",tracking=True)
    dias_literal_c=fields.Float(string="Cant. dias L. C",compute="_get_minimo_a_liquidar",store=True)
    @api.depends('employee_id','fecha')
    def _compute_salario_promedio(self):
        for rec in self:
            if rec.fecha:
                begintime=rec.fecha -relativedelta(months=3)
                nominas=rec.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),('date_from', '>=', begintime),('date_to', '<=', rec.fecha),('is_vacation','=',False),('is_anihilation','=',False),('is_utility','=',False),('type_struct_category','in',['normal','especial'])])

            else:
                begintime=TODAY -relativedelta(months=3)
                nominas=rec.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),('date_from', '>=', begintime),('date_to', '<=', TODAY),('is_vacation','=',False),('is_anihilation','=',False),('is_utility','=',False),('type_struct_category','in',['normal','especial'])])
            sal=sum(sum(y.total for y in x.line_ids.filtered(lambda line: line.category_id.code == 'BASIC')) for x in nominas)
            
            rec.salario_promedio=sal/90 if sal>0 else 0
    @api.depends("contract_id")
    def _compute_is_variable(self):
        for rec in self:
            rec.is_variable=rec.contract_id.is_variable_wage
    @api.depends("employee_id")
    def _get_vacaciones_disfrutada(self):
        for rec in self:
            vacas=rec.env["hr.payslip"].search([('is_vacation','=',True),('employee_id','=',rec.employee_id.id),('state','not in',['cancel','draft'])])
            rec.vacaciones_disfrutadas=vacas
    @api.depends("employee_id","company_id","total_vacciones","vacaciones_disfrutadas","ao","mes",'dia')
    def _get_dias_vacaciones_utili(self):
        for rec in self:
            dias_vaca=0
            restantes=0
            tomadas=len(rec.vacaciones_disfrutadas)
            if rec.total_vacciones>0:
                restantes=rec.total_vacciones-tomadas
            
            if rec.mes>=1:
                restantes+=1
            rec.vacaciones_restantes=restantes
            if rec.ao>=2 and rec.vacaciones_restantes:
                for i in range(1,restantes+1):
                    aux=rec.company_id.dias_vac_base + rec.employee_id.dias_bono-i
                    dias_vaca+=aux if aux>=rec.company_id.dias_vac_base else rec.company_id.dias_vac_base
            else:
                dias_vaca=rec.company_id.dias_vac_base*restantes
            dias_vaca+= ((rec.company_id.dias_vac_base/12)*rec.mes if rec.mes else 0 )

            rec.days_of_vacations=dias_vaca
            ultima_utility=rec.env["hr.payslip"].search([('employee_id','=',rec.employee_id.id),('is_utility','=',True),('state','not in',['cancel'])])
            number_of_used_util=sum(ultima_utility.mapped('line_ids').filtered(lambda x: x.code=='Uti_fracc').mapped('quantity'))
            if ultima_utility:

                time_since_last_u=(rec.ao*360+rec.mes*30+rec.dia)-(number_of_used_util*(360/rec.company_id.cant_dias_utilidades))
            else:
                
                time_since_last_u=(rec.ao*360)+(rec.mes*30)+rec.dia
            
            rec.days_of_utilidades=(rec.company_id.cant_dias_utilidades/360)*(time_since_last_u) +rec.employee_id.offset_days_utils
            rec.total_utilidades=rec.days_of_utilidades*rec.sal_diario

    
    @api.depends("employee_id")
    def _get_last_prestacion_line(self):
        for rec in self:
            rec.Last_prestacion= rec.env["hr.prestaciones.employee.line"].search([('parent_id','=',rec.employee_id.id)],limit=1,order="id desc")

    @api.depends("employee_id","fecha")
    def _get_sal_diario(self):
        for rec in self:
                if rec.vacation_payslip:
                    nominas=rec.env['hr.payslip'].search([('is_anihilation','=',False),('employee_id','=',rec.employee_id.id)]).filtered(lambda x:x.date_to.month==rec.fecha.month and x.id!=rec.vacation_payslip.id)
                else:
                    nominas=rec.env['hr.payslip'].search([('is_anihilation','=',False),('employee_id','=',rec.employee_id.id)]).filtered(lambda x:x.date_to.month==rec.fecha.month)
                total=sum(x.total  for x in nominas.mapped("line_ids").filtered(lambda x: x.category_id.code=="BASIC"))

                contrato=rec.employee_id.contract_id #obtenido contrato
                if total<contrato.wage:
                    sal_mensual=contrato.wage
                else:
                    sal_mensual=total #obtenido sal_mensual
                sal_diario=sal_mensual/30 #obtenido sal_diario
                rec.alicuota_utilidades=(sal_diario*rec.env.company.cant_dias_utilidades)/360 #obtenido utilidades 
                dias_vacaciones=rec.env.company.dias_vac_base + rec.employee_id.dias_bono
                rec.alicuota_vacaciones=(sal_diario*dias_vacaciones)/360 #obtenido vacaciones
                sal_dia_total=sal_diario+rec.alicuota_vacaciones+rec.alicuota_utilidades #tenemos diario integral
                if sal_dia_total<1:  # mejorar comprobacion, que pasa si es menos del salario?
                    rec.sal_diario=rec.contract_id.wage/30
                else:
                    rec.sal_diario=round(sal_dia_total,4)
                
    @api.depends("sal_diario","ao","mes")
    def _get_minimo_a_liquidar(self):
        for rec in self:
            rec.minimo_a_liquidar=(rec.sal_diario*(30*rec.ao +rec.get_dias_antiguedad_minimo_liquidar()))+(rec.sal_diario*(30/12)*(rec.mes if rec.mes>6 else 0))
            rec.dias_literal_c=round((30*rec.ao +rec.get_dias_antiguedad_minimo_liquidar())+((30/12)*(rec.mes if rec.mes>6 else 0)),4)
    @api.depends('total_liquidar','minimo_a_liquidar')
    def _comparate_liquidates(self):
        for rec in self:
            if rec.prestacion_total<rec.minimo_a_liquidar:
                    rec.monto_art92_liq=rec.minimo_a_liquidar    
            else:
                    rec.monto_art92_liq=rec.prestacion_total
    def get_dias_antiguedad_minimo_liquidar(self):
        for rec in self:
            vueltas=rec.ao-1
            result=0
            while vueltas>0:
                result+=2
                vueltas-=1
            return result
    
    def action_go_to_vacaciones(self):

        return {
            'type':'ir.actions.act_window',
            'name': 'Vacacion por liquidacion',
            'res_model':'hr.payslip',
            'view_mode':'form',
            'res_id':self.vacation_payslip.id,
            'target':'current'
        }

    def action_go_to_liquidation(self):

        return {
            'type':'ir.actions.act_window',
            'name': 'Nómina por liquidacion',
            'res_model':'hr.payslip',
            'view_mode':'form',
            'res_id':self.terminated_payslip.id,
            'target':'current'
        }
    def liquidar(self):
        for rec in self:
            if rec.vacation_payslip and rec.vacation_payslip.state not in ['done']:
                rec.vacation_payslip.sudo().action_payslip_cancel()
                rec.vacation_payslip.sudo().unlink() 
            if rec.terminated_payslip and rec.terminated_payslip.state not in ['done']:
                rec.terminated_payslip.sudo().action_payslip_cancel()
                rec.terminated_payslip.sudo().unlink() 
            if rec.liquidado:
                rec.liquidado.sudo().unlink()
            #Crear nominas de vacaciones
            if not rec.struct_vacaciones:
                raise ValidationError(f"Defina una estructura de vacaciones en configuración")
            if not rec.struct_vacaciones.journal_id:
                raise ValidationError(f"Defina una diario para la estructura {rec.struct_vacaciones.name}")
            if not rec.struct_liqidation:
                raise ValidationError(f"Defina una estructura de liquidacion en configuración")
            if not rec.struct_liqidation.journal_id:
                raise ValidationError(f"Defina una diario para la estructura {rec.struct_liqidation.name}")
            if  len(rec.struct_liqidation.input_line_type_ids)<6:
                raise ValidationError(f"La estructura de liquidación {rec.struct_liqidation.name} no posee las suficientes entradas adicionales, por favor agregue {6-len(rec.struct_liqidation.input_line_type_ids)}")
            # if not any([self.prestacion_total,self.minimo_a_liquidar]):
            #     raise ValidationError("Existe un error en las prestaciones, quizas un dato faltante.")
            rec._comparate_liquidates()
            rec.total_liquidar=rec.monto_art92_liq
            if (rec.vacaciones_restantes or rec.days_of_vacations):
                try:
                    vacanom=rec.env["hr.payslip"].create({
                        'employee_id':rec.employee_id.id,
                        'is_vacation':True,
                        'date_from':rec.fecha,
                        'date_to':rec.fecha+ relativedelta(days=rec.days_of_vacations),
                        'anno_vacaciones_designado':rec.fecha.year,
                        'contract_id':rec.contract_id.id,
                        'struct_id':rec.struct_vacaciones.id,
                        'pay_type':'deposito',
                        'name': f"Vacaciones por liquidacion - {rec.name} - {rec.fecha.strftime('%B de %Y')}",
                        'company_id':rec.company_id.id,
                        'journal_id':rec.struct_vacaciones.journal_id.id,
                        'company_id':rec.company_id.id,
                        'liquidation_id':rec.id
                    })
                    vacanom.action_refresh_from_work_entries()
                    vacanom._onchange_is_vacation(rec.days_of_vacations)
                    vacanom.compute_sheet(rec.days_of_vacations)
                    vacanom.name=f"Vacaciones por liquidacion - {rec.name} - {rec.fecha.strftime('%B de %Y')}"
                    rec.vacaciones_disfrutadas+=vacanom
                    rec.vacation_payslip=vacanom
                except:
                    raise UserError("estas creando la vacacion pero hay algun dato mal")
            
            #liquidaciones
            liquidanom=self.env["hr.payslip"].create({
                    'employee_id':rec.employee_id.id,
                    'is_vacation':False,
                    'is_anihilation':True,
                    'date_from':rec.employee_id.fecha_inicio,
                    'date_to':rec.fecha,
                    'contract_id':rec.contract_id.id,
                    'struct_id':rec.struct_liqidation.id,
                    'pay_type':'deposito',
                    'name': f"Liquidacion - {rec.name} - {rec.fecha.strftime('%B de %Y')}",
                    'company_id':rec.company_id.id,
                    'liquidation_id':rec.id,
                    'journal_id':rec.struct_liqidation.journal_id.id
                })
            
            liquidanom._onchange_employee()
            liquidanom.input_line_ids[0].amount=rec.total_utilidades
            liquidanom.input_line_ids[1].amount=rec.intereses_prestaciones
            liquidanom.input_line_ids[2].amount=rec.prestacion_total
            liquidanom.input_line_ids[3].amount=rec.minimo_a_liquidar
            liquidanom.input_line_ids[4].amount=rec.monto_art92_liq if rec.motivo=="despido" else 0
            liquidanom.input_line_ids[5].amount=rec.adicionales
            liquidanom.compute_sheet()
            liquidanom.name=f"Liquidacion - {rec.name} - {rec.fecha.strftime('%B de %Y')}"
            rec.terminated_payslip=liquidanom

            rec.great_sumatory=rec.total_utilidades+rec.intereses_prestaciones+rec.total_liquidar
            rec.liquidado=rec.env['hr.prestaciones.employee.line'].create({
                    'line_type':'liquidacion',
                    'parent_id': rec.employee_id.id,
                    'company_id':rec.company_id.id,
                    'fecha':rec.fecha,
                    'contract_id':rec.contract_id.id,
                    'sal_mensual':False,
                    'sal_diario':False,
                    'antiguedad':False,
                    'antiguedad_adicional':False,
                    'utilidades':False,
                    'vacaciones':False,
                    'antiguedad80':False,
                    'total_diario':False,
                    'prestaciones_mes':False,
                    'anticipos_otorga':rec.total_liquidar, #falta
                    'prestaciones_acu':False,
                    'tasa_activa':False,
                    'intereses':False,
                    'intereses_acum':rec.intereses_prestaciones,
                    'presta_e_inte':rec.intereses_prestaciones+rec.total_liquidar,
                    
                })
            rec.env['hr.prestaciones.employee.line'].create({
                    'line_type':'clean',
                    'parent_id': rec.employee_id.id,
                    'company_id':rec.company_id.id,
                    'fecha':rec.fecha,
                    'contract_id':rec.contract_id.id,
                    'sal_mensual':False,
                    'sal_diario':False,
                    'antiguedad':False,
                    'antiguedad_adicional':False,
                    'utilidades':False,
                    'vacaciones':False,
                    'antiguedad80':False,
                    'total_diario':False,
                    'prestaciones_mes':False,
                    'anticipos_otorga':False, #falta
                    'prestaciones_acu':False,
                    'tasa_activa':False,
                    'intereses':False,
                    'intereses_acum':False,
                    'presta_e_inte':False,
                    
                })
            rec.contract_id.state="close"
            rec.employee_id.fecha_fin=rec.fecha
            

                


class HRLiquidacionLote(models.Model):
    _name="hr.liquidacion.lote"
    _description="Lo mismo pero por lotes"

    liquidacion_line_id=fields.One2many("hr.liquidacion","lote_id")
    employee_ids=fields.Many2many("hr.employee")
    company_id=fields.Many2one("res.company",default=lambda self: self.env.company)

    name=fields.Char(default=f"Lote de Liquidaciones {TODAY.strftime('%B de %Y')}")

    fecha=fields.Date(default=date(TODAY.year,TODAY.month,monthrange(TODAY.year, TODAY.month)[1]))

    department_id=fields.Many2one('hr.department', "Departamento")
    cargo_id=fields.Many2one('hr.job',"Cargo")
    category_id_filter=fields.Many2one('hr.employee.category',string="Categoria Empleado")

    @api.onchange('department_id','cargo_id','category_id_filter')
    def onchange_filters(self):
        for rec in self:
            domain=[]
            if rec.category_id_filter:
                domain.append(('category_ids','=',rec.category_id_filter.id))
            if rec.department_id:
                domain.append(('department_id','=',rec.department_id.id))
            if rec.cargo_id:
                domain.append(('contract_id.job_id','=',rec.job_id_filter.id))

            empleados=False
            if len(domain)>0:
                empleados=self.env['hr.employee'].search(domain)
            if empleados:
                rec.employee_id=empleados



# class HRLiquidacionLine(models.Model):
#     _name = 'hr.employee.liquidation.line'

#     _description = "linea para la creacion de los datos para liquidacion,yeah that"

#     parent_id=fields.Many2one("hr.liquidacion")

#     rule=fields.many2one("hr.salary.rule")



#     monto_total=fields.Float()


