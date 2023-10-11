# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta
from .test import scrap_from_BCV_Prestaciones, numero_to_letras,convierte_cifra
from calendar import monthrange


TODAY=date.today()
NOW=fields.Datetime.now()
class HrEmployeeEu(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee','mail.thread', 'mail.activity.mixin']

    def create_prestacion(self):
        employees=self.env['hr.employee'].search([('fecha_inicio','!=',False)]).filtered(lambda x:  int(date.today().strftime("%d"))-1 <= int(x.fecha_inicio.strftime("%d")) <= int(date.today().strftime("%d"))+1)

        prestaciones=self.env['hr.prestaciones.employee.line'].search([('line_type','=','prestacion')]).filtered(lambda x:x.fecha.strftime("%m%Y") == date.today().strftime("%m%Y")) 
        for e in employees:
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
                    prestaciones_lines=self.env["hr.prestaciones.employee.line"].search([('parent_id','=',e.id),('company_id','=',e.company_id.id)])
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
                                'debit':intereses,
                                'move_id':apunte.id
                            })
                            line.append({
                                'account_id':e.company_id.asiento_interes_paga.id,
                                'name': f"intereses {date.today()} - {e.name}",
                                'credit':intereses,
                                'move_id':apunte.id
                            })
                        if prestaciones_mes>0:
                            line.append({
                                'account_id':e.company_id.asiento_prestaciones.id,
                                'name': f"Prestación {date.today()} - {e.name}",
                                'debit':prestaciones_mes,
                                'move_id':apunte.id
                            })
                            line.append({
                                'account_id':e.company_id.asiento_antiguedad_p.id,
                                'name': f"Prestación {date.today()} - {e.name}",
                                'credit':prestaciones_mes,
                                'move_id':apunte.id
                            })
                if e.company_id.journal_for_prestaciones:
                    for li in line:
                        apunte.line_ids+=self.env['account.move.line'].create(li)
    def numero_to_letras_contract(self,numero):
        return numero_to_letras(numero)
    def generate_work_entries3(self):
        for rec in self:
            rec.sudo().contract_id.generate_and_change_entries(fields.Datetime.to_datetime(rec.contract_id.date_start), fields.Datetime.to_datetime(rec.contract_id.date_end) if rec.contract_id.date_end else (NOW+relativedelta.relativedelta(year=1)))

    def destroy_and_regen(self):
        self.env['hr.work.entry'].search([]).sudo().unlink()
        
        for rec in self.env['hr.employee'].search([]):

            rec.sudo().contract_id.generate_and_change_entries(fields.Datetime.to_datetime(rec.contract_id.date_start), fields.Datetime.to_datetime(rec.contract_id.date_end) if rec.contract_id.date_end else (NOW+relativedelta.relativedelta(year=1)))

    def destroy_and_regen_per_employee(self):
        for rec in self:
            self.env['hr.work.entry'].search([('employee_id','=',rec.id)]).sudo().unlink()
            rec.sudo().contract_id.generate_and_change_entries(fields.Datetime.to_datetime(rec.contract_id.date_start), fields.Datetime.to_datetime(rec.contract_id.date_end) if rec.contract_id.date_end else (NOW+relativedelta.relativedelta(month=2)))


    def destroy_repetidas(self):
        entradasdup=self.env['hr.work.entry'].search([('state','=','conflict'),('work_entry_type_id','=',1)])
        passed=self.env['hr.work.entry']
        for rec in entradasdup:
            if passed.filtered(lambda x:x.date_start==rec.date_start and x.date_stop==rec.date_stop and x.employee_id==rec.employee_id):
                rec.sudo().unlink()
            else:
                passed+=rec


    
    




    def vacation_returns(self):

        employees_on_vacation=self.env['hr.employee'].search([('in_vacations_till','!=',False)])
        for e in employees_on_vacation:
            if e.in_vacations_till<=TODAY:
                e.in_vacations=False
                

    
    prefered_pay_type=fields.Selection([
        ('deposito','DEPOSITO'),
        ('cheque','CHEQUE'),
        ('pagomovil','PAGO MÓVIL'),
        ('efectivo','EFECTIVO'),
        ('mixta','MIXTA')
    ],required=True,default='deposito',tracking=True)
    autoriza_retencion=fields.Boolean(default=True, required=True,string="Autoriza la retención",tracking=True)
    num_sso=fields.Char("Código de SSO",tracking=True)
    liquidado_fecha=fields.Char("Código de SSO",tracking=True)
    in_vacations_till=fields.Date('En vacaciones hasta',tracking=True)
    in_vacations=fields.Boolean('En vacaciones hasta',tracking=True)
    in_vacations_since=fields.Date('En vacaciones desde',tracking=True)
    offset_days_utils=fields.Float("Diferencial dias de utilidades",tracking=True)
    offset_vacaciones=fields.Integer("Diferencial vacaciones",tracking=True)
    
    has_pc=fields.Selection([
        ('yes','Sí'),
        ('no','No')
    ],string="¿Posee computador propio?",tracking=True)

    type_conection=fields.Selection([
        ('fiber','Fibra'),
        ('adsl','ADSL'),
        ('inalambrico','Inalambrico'),
        ('movil','Móvil')
    ],string="¿Tipo de conexión a Internet?",tracking=True)

    isp_provider=fields.Char(string="Proveedor de ISP",tracking=True)

    dias_bono=fields.Integer(compute="_compute_dias_bono",tracking=True)

    #datos extra para los empleados
    birthday_month=fields.Integer("mes de cumpleaños",compute="_this_month_birthed_the_bird",store=True)
    discapacidad=fields.Boolean("¿Posee alguna discapacidad",tracking=True)
    tipo_discapacidad=fields.Many2many('discapacity',string="Discapacidad",tracking=True)
    tipo_origen=fields.Selection([('mestizo','Mestizo'),('extranjero','Extranjero'),('indio','Aborigen')],tracking=True)
    dotaciones=fields.Float("Dotaciones",tracking=True)
    fecha_inicio = fields.Date("Fecha de Ingreso", required=False,default=TODAY,tracking=True)
    vacaciones_total=fields.Integer(compute='_compute_num_vacaciones',tracking=True)
    journey_group_id=fields.Many2one('hr.employee.journey.group',tracking=True)
    talla_shirt= fields.Char("Talla Camisa/franela",tracking=True)
    talla_pantaloon= fields.Char("Talla Pantalon",tracking=True)
    talla_shoes= fields.Char("Talla Zapatos",tracking=True)
    historico_trabajos=fields.One2many("job.history.line",'parent_id')
    personal_email = fields.Char('Correo electrónico personal', size=240, required=False)
    is_delegado=fields.Boolean("¿Es delegado Inpsasel?",tracking=True)
    nationality = fields.Selection([
        ('V', 'Venezolano'), 
        ('E', 'Extranjero')]
        , string='Tipo documento', required=False,default="V",tracking=True)
    bonificaciones_per_employee=fields.One2many("bonification.per.employee","employee_id",string="Bonificaciones",tracking=True)
    comisiones_per_employee=fields.One2many("comisiones.per.employee","employee_id",string="Comisiones",tracking=True)    
    has_autorized=fields.Boolean('Usar autorizado')
    bank_autorizate=fields.Many2one('res.bank',string="Banco del autorizado")
    name_autorizate=fields.Char("Nombre Autorizado")
    ci_autorizate=fields.Char("Cedula del autorizado")
    account_number_autorizate=fields.Char("Cuenta Autorizado",digits=20)
    sindicalizado=fields.Boolean("¿Esta sindicalizado?")
    is_carrier_woman=fields.Boolean("¿Esta embarazada?")
    tipo_empleado=fields.Selection([('1','De Dirección'),('2','De Inspección o Vigilancia'),
                                    ('3','Aprendiz Inces'),('4','Pasante'),
                                    ('5','Trabajador Calificado'),('6','Trabajador no Calificado')],"Tipo de empleado")
    has_health_certificate=fields.Boolean("¿Tiene Certificado de Salud?")
    health_certificate_due_date=fields.Date("Fecha de vencimiento de Certificado")
    puntual=fields.Boolean("Puntual",tracking=True,default=True)
    exemplar=fields.Boolean("Ejemplar",tracking=True,default=True)
    vacaciones_disfrutadas=fields.Integer(compute="_get_vacaciones_disfrutada", string="Vacaciones Disfrutadas",store=True)
    has_vacations_loose=fields.Boolean(compute="_get_vacaciones_disfrutada", string="Vacaciones Pendientes")
    #ya que multiples cosas pueden pasar, el job title cambiara en un write
    @api.depends("slip_ids","slip_ids.state",'vacaciones_disfrutadas','vacaciones_total','fecha_inicio')
    def _get_vacaciones_disfrutada(self):
        for rec in self:
            rec.has_vacations_loose=False
            vacas=len(rec.slip_ids.filtered(lambda x: x.is_vacation and x.state not in ['cancel','draft']))
            rec.vacaciones_disfrutadas=vacas
            firstmonthbefore=TODAY-relativedelta.relativedelta(months=1)
            if rec.fecha_inicio.month==firstmonthbefore.month and rec.vacaciones_total>0:
                rec.has_vacations_loose=True
    def _this_month_birthed_the_bird(self):
        for rec in self:
            if rec.birthday:
                rec.birthday_month=rec.birthday.month
            else:
                rec.birthday_month=0

    def company_onchange_natio_state_city(self):
        for rec in self:
            rec.country_id=rec.company_id.country_id
            rec.state_id=rec.company_id.state_id
    
    
    @api.model
    def _name_search(self, name, args = None, operator = "ilike", limit = 50, name_get_uid = None):
        args = args or []

        domain = [
            *['|'] * 1,
            *map(
                lambda field: (field, operator, name),
                ['name', 'emp_id']
            ),
        ] if name else []

        return self._search(
            domain + args, 
            limit = limit, 
            access_rights_uid = name_get_uid
        )
    # category_worker=fields.Many2one('employee.category',related="contract_id.category_worker")
    def action_create_vaciones(self):
        for rec in self:
                        
            vacaciones_totales=rec.env['list.vacation'].search([('employee_id','=',rec.id)],order="corresponde_a desc")
            if vacaciones_totales:
                num= rec.vacaciones_total-len(vacaciones_totales)
                for an in range(0,num):
                    rec.env['list.vacation'].sudo().create({'employee_id':rec.id})
            else:
                num= rec.vacaciones_total
                for an in range(0,num):
                    rec.env['list.vacation'].sudo().create({'employee_id':rec.id})


    def action_go_to_prestaciones(self):

        return {
            'type':'ir.actions.act_window',
            'name': 'Prestaciones del trabajador',
            'res_model':'hr.prestaciones.employee.line',
            'domain':[('parent_id','=',self.id)],
            'view_mode':'tree',
            'target':'current'
        }

    def action_go_to_vacaciones(self):

        return {
            'type':'ir.actions.act_window',
            'name': 'Vacaciones del trabajador',
            'res_model':'hr.payslip',
            'domain':[('employee_id','=',self.id),('is_vacation','=',True)],
            'view_mode':'tree',
            'target':'current'
        }



    @api.depends("ano_antig",'mes_antig','offset_vacaciones')
    def _compute_num_vacaciones(self):
        for rec in self:
            if rec.ano_antig>0:
                rec.vacaciones_total=rec.ano_antig
            elif rec.mes_antig>=6:
                rec.vacaciones_total=1
            else:
                rec.vacaciones_total=0
            if rec.offset_vacaciones :
                rec.vacaciones_total=rec.vacaciones_total+rec.offset_vacaciones
                if rec.vacaciones_total<0:
                    rec.vacaciones_total=0

    @api.depends("ano_antig")
    def _compute_dias_bono(self):
        for rec in self:
            if rec.ano_antig>=2:
                rec.dias_bono=1+(rec.ano_antig-2)
            else:
                rec.dias_bono=0

    def export_dotation(self):


        employee_ids='_'.join(map(str,self.ids))
        
        return {
            'type'  : 'ir.actions.act_url',
            'url'   : f"/dotations/{employee_ids}",
            'target': 'new',
            'res_id': self.ids,
            
        }


    def export_faov(self):

            

        # if any(slip.employee_id.account_number_2[:4] != self.bank_code  if slip.employee_id.account_number_2 else False for slip in self.slip_ids ):
        #     raise UserError("Hay trabajadores cuya cuenta bancaria es diferente al banco deseado, revise nuevamente")
        # lista=[]
        # for id in self.ids:
        #     lista.append(str(id))
        employee_ids='_'.join(map(str,self.ids))
        
        return {
            'type'  : 'ir.actions.act_url',
            'url'   : f"/faov/{employee_ids}",
            'target': 'new',
            'res_id': self.ids,
            
        }
    def export_mintra_fijo(self):

            

        # if any(slip.employee_id.account_number_2[:4] != self.bank_code  if slip.employee_id.account_number_2 else False for slip in self.slip_ids ):
        #     raise UserError("Hay trabajadores cuya cuenta bancaria es diferente al banco deseado, revise nuevamente")
        # lista=[]
        # for id in self.ids:
        #     lista.append(str(id))
        employee_ids='_'.join(map(str,self.ids))
        
        return {
            'type'  : 'ir.actions.act_url',
            'url'   : f"/mintraf/{employee_ids}",
            'target': 'new',
            'res_id': self.ids,
            
        }
    def export_mintra_variable(self):

            

        # if any(slip.employee_id.account_number_2[:4] != self.bank_code  if slip.employee_id.account_number_2 else False for slip in self.slip_ids ):
        #     raise UserError("Hay trabajadores cuya cuenta bancaria es diferente al banco deseado, revise nuevamente")
        # lista=[]
        # for id in self.ids:
        #     lista.append(str(id))
        employee_ids='_'.join(map(str,self.ids))
        
        return {
            'type'  : 'ir.actions.act_url',
            'url'   : f"/mintrav/{employee_ids}",
            'target': 'new',
            'res_id': self.ids,
            
        }

class HrEmployeeEuP(models.Model):
    _name = 'hr.employee.public'
    _inherit = ['hr.employee.public','mail.thread', 'mail.activity.mixin']
    prefered_pay_type=fields.Selection([
        ('deposito','DEPOSITO'),
        ('cheque','CHEQUE'),
        ('pagomovil','PAGO MÓVIL'),
        ('efectivo','EFECTIVO'),
        ('mixta','MIXTA')
    ],required=True,default='deposito')

    autoriza_retencion=fields.Boolean(default=True, required=True,string="Autoriza la retención")
    num_sso=fields.Char("Código de SSO")
    liquidado_fecha=fields.Char("Código de SSO")
    offset_days_utils=fields.Float("Diferencial dias de utilidades")
    offset_vacaciones=fields.Integer("Diferencial vacaciones")
    has_pc=fields.Selection([
        ('yes','Sí'),
        ('no','No')
    ],string="¿Posee computador propio?")
    in_vacations_till=fields.Date('En vacaciones hasta',tracking=True)
    in_vacations=fields.Boolean('En vacaciones hasta',tracking=True)

    in_vacations_since=fields.Date('En vacaciones desde',tracking=True)

    type_conection=fields.Selection([
        ('fiber','Fibra'),
        ('adsl','ADSL'),
        ('inalambrico','Inalambrico'),
        ('movil','Móvil')
    ],string="¿Tipo de conexión a Internet?")

    isp_provider=fields.Char(string="Proveedor de ISP")

    dias_bono=fields.Integer(compute="_compute_dias_bono")

    #datos extra para los empleados
    birthday_month=fields.Integer("mes de cumpleaños",compute="_this_month_birthed_the_bird",store=True)
    discapacidad=fields.Boolean("¿Posee alguna discapacidad")
    tipo_discapacidad=fields.Many2many('discapacity',string="Discapacidad")
    tipo_origen=fields.Selection([('mestizo','Mestizo'),('extranjero','Extranjero'),('indio','Aborigen')])
    dotaciones=fields.Float("Dotaciones")
    fecha_inicio = fields.Date("Fecha de Ingreso", required=False,default=TODAY)
    vacaciones_total=fields.Integer(compute='_compute_num_vacaciones')
    journey_group_id=fields.Many2one('hr.employee.journey.group')
    talla_shirt= fields.Char("Talla Camisa/franela")
    talla_pantaloon= fields.Char("Talla Pantalon")
    talla_shoes= fields.Char("Talla Zapatos")
    historico_trabajos=fields.One2many("job.history.line",'parent_id')
    personal_email = fields.Char('Correo electrónico personal', size=240, required=False)
    rif = fields.Char('Rif', size=11, required=False)
    is_delegado=fields.Boolean("¿Es delegado Inpsasel?")
    nationality = fields.Selection([
        ('V', 'Venezolano'), 
        ('E', 'Extranjero')]
        , string='Tipo documento', required=False,default="V")
    bonificaciones_per_employee=fields.One2many("bonification.per.employee","employee_id",string="Bonificaciones")
    comisiones_per_employee=fields.One2many("comisiones.per.employee","employee_id",string="Comisiones")    
    has_autorized=fields.Boolean('Usar autorizado')
    bank_autorizate=fields.Many2one('res.bank',string="Banco del autorizado")
    name_autorizate=fields.Char("Nombre Autorizado")
    ci_autorizate=fields.Char("Cedula del autorizado")
    account_number_autorizate=fields.Char("Cuenta Autorizado",digits=20)
    sindicalizado=fields.Boolean("¿Esta sindicalizado?")
    is_carrier_woman=fields.Boolean("¿Esta embarazada?")
    tipo_empleado=fields.Selection([('1','De Dirección'),('2','De Inspección o Vigilancia'),
                                    ('3','Aprendiz Inces'),('4','Pasante'),
                                    ('5','Trabajador Calificado'),('6','Trabajador no Calificado')],"Tipo de empleado")
    puntual=fields.Boolean("Puntual",tracking=True)
    exemplar=fields.Boolean("Ejemplar",tracking=True)
    vacaciones_disfrutadas=fields.Integer( string="Vacaciones Disfrutadas")
    has_health_certificate=fields.Boolean("¿Tiene Certificado de Salud?")
    health_certificate_due_date=fields.Date("Fecha de vencimiento de Certificado")

    has_vacations_loose=fields.Boolean(compute="_get_vacaciones_disfrutada", string="Vacaciones Pendientes")
    #ya que multiples cosas pueden pasar, el job title cambiara en un write
    @api.depends('vacaciones_disfrutadas','vacaciones_total','fecha_inicio')
    def _get_vacaciones_disfrutada(self):
        for rec in self:
            rec.has_vacations_loose=False
            firstmonthbefore=TODAY-relativedelta.relativedelta(months=1)
            if rec.fecha_inicio.month==firstmonthbefore.month:
                rec.has_vacations_loose=True
    @api.model
    def _name_search(self, name, args = None, operator = "ilike", limit = 50, name_get_uid = None):
        args = args or []

        domain = [
            *['|'] * 1,
            *map(
                lambda field: (field, operator, name),
                ['name', 'emp_id']
            ),
        ] if name else []

        return self._search(
            domain + args, 
            limit = limit, 
            access_rights_uid = name_get_uid
        )
class HrSon(models.Model):
    _inherit = "hr.son"

    talla_shirt= fields.Char("Talla Camisa/franela")
    talla_pantaloon= fields.Char("Talla Pantalon")
    talla_shoes= fields.Char("Talla Zapatos")
    nivel_instruccion= fields.Char("Nivel de Instrución")

class HrDiscapacity(models.Model):
    _name = "discapacity"

    name=fields.Char("Nombre")
    tipo_disc=fields.Selection([('visual','Visual'),('auditive','Auditiva'),('intelectual','Intelectual'),
                                ('mental','Mental'),('muscular','Muscular'),('accident','Accidente'),
                                ('illness','Enfermedad'),('other','Otra')],string="Tipo de discapacidad")
    descripcion=fields.Char("Descripción")
class HrPrestacionLines(models.Model):
    _name = "hr.prestaciones.employee.line"

    name=fields.Char(compute="_naming_the_p_line")
    comprometida=fields.Boolean(string="Comprometida para pago")
    line_type=fields.Selection([('prestacion','prestacion'),('anticipo','anticipo'),('liquidacion','liquidacion'),('clean','clean')])
    parent_id=fields.Many2one('hr.employee')
    company_id=fields.Many2one('res.company',default=lambda self: self.env.company)
    fecha=fields.Date()
    contract_id=fields.Many2one('hr.contract')
    sal_mensual=fields.Float("saldo mensual")
    sal_diario=fields.Float("saldo diario")
    antiguedad=fields.Float()
    antiguedad_adicional=fields.Float()
    utilidades=fields.Float()
    vacaciones=fields.Float()
    antiguedad80=fields.Float()
    total_diario=fields.Float()
    prestaciones_mes=fields.Float()
    anticipos_otorga=fields.Float()
    porcentaje=fields.Float(string="%")
    prestaciones_acu=fields.Float(string="prest. acum.")
    tasa_activa=fields.Float()
    intereses=fields.Float()
    intereses_acum=fields.Float(string="int. acum.")
    presta_e_inte=fields.Float(string="Acum.")
    parent_lote_prest=fields.Many2one('hr.prestaciones')
    parent_lote_anticip=fields.Many2one('hr.anticipos')
    is_anticipo_intereses=fields.Boolean()
    @api.depends("parent_id",'fecha')
    def _naming_the_p_line(self):
        for rec in self:
            rec.name=f"Linea estado de prestaciones de {rec.parent_id.name} para el {rec.fecha}"

class HRJobHistorialLines(models.Model):
    _name="job.history.line"

    parent_id=fields.Many2one('hr.employee',"Empleado")
    job_title=fields.Char("Puesto de Trabajo")
    date_change=fields.Date("Fecha de cambio")

