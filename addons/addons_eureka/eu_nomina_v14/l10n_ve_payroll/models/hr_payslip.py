# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import models, fields,api
from odoo.osv import expression
from math import ceil
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from calendar import monthrange,weekday
from odoo.tools import float_compare, float_is_zero

TODAY=date.today()

class HRStructureAdd(models.Model):
    _name="hr.payroll.structure"
    _inherit = ["hr.payroll.structure",'mail.thread', 'mail.activity.mixin']

    use_comision=fields.Boolean("Utiliza comisiones",tracking=True)
    use_variable_bonifications=fields.Boolean("Utiliza Bonificaciones Variables",tracking=True)
    company_id = fields.Many2one('res.company',string="Compañía",tracking=True,invisible=True)
    struct_category=fields.Selection(selection_add=[('vacation', 'Vacaciones'),('advance','Adelanto'),('utilities','Utilidades')],ondelete={'vacation':'set default','advance':'set default','utilities':'set default'},default="normal",tracking=True)
    use_for_proyection=fields.Boolean('Usar para previsualizar',tracking=True)
    auto_post=fields.Boolean("Auto Publicar asientos",tracking=True)
class HRSalaryRule(models.Model):
    _name="hr.salary.rule"
    _inherit = ["hr.salary.rule",'mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company',string="Compañía", related="struct_id.company_id",tracking=True,invisible=True)
    account_debit = fields.Many2one('account.account', 'Cuenta Deudora',
                                    domain=['|',('deprecated', '=', False),('company_id','=',company_id),('company_id','=',False)], company_dependent=True,tracking=True)
    account_credit = fields.Many2one('account.account', 'Cuenta Acreedora',
                                     domain=['|',('deprecated', '=', False),('company_id','=',company_id),('company_id','=',False)], company_dependent=True,tracking=True)
    category_id =fields.Many2one('hr.salary.rule.category',tracking=True)
    name=fields.Char(tracking=True)
    code=fields.Char(tracking=True)
    sequence=fields.Integer(tracking=True)
    condition_select=fields.Selection(tracking=True)
    amount_select=fields.Selection(tracking=True)
    amount_fix=fields.Float(tracking=True)
    quantity=fields.Char(tracking=True)
    # apears_on_payslip=fields.Boolean(tracking=True)
    struct_id=fields.Many2one('hr.payroll.structure',tracking=True)
    active=fields.Boolean(tracking=True)
    amount_python_compute=fields.Text(tracking=True)
    condition_python=fields.Text(tracking=True)
    account_debit=fields.Many2one('account.account',tracking=True)
    account_credit=fields.Many2one('account.account',tracking=True)
    appears_on_payslip_receipt=fields.Boolean("Aparece en Recibo G.",default=True)

class HRPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip','mail.thread', 'mail.activity.mixin']

    currency_id_dif = fields.Many2one("res.currency", 
        string="Referencia en Divisa",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),)
    

    apuntes_contables = fields.One2many(related='move_id.line_ids', readonly=True,tracking=True)
    has_incidencias=fields.Boolean(readonly=True,string="Tiene incidencias")
    sal_comple = fields.Float(related="contract_id.complemento", string="Complemento Salario",store=True)
    type_struct_category=fields.Selection(related="struct_id.struct_category")
    tax_today= fields.Float(readonly=False, compute="_tax_today",store=True, string="Tasa del Día",tracking=True) 
    finmes=fields.Boolean(compute="_calcular_lunes")
    hours_exday=fields.Float(string="Horas extra Diurnas", compute="_compute_extra_hours")
    hours_exnight=fields.Float(string="Horas extra Nocturnas", compute="_compute_extra_hours")
    # ignorate_on_vacations=fields.Boolean(string="Ignorar en Vacaciones")
    horas_nocturnas=fields.Float(string="Horas nocturnas", compute="_calcular_lunes", store=True)
    horas_diurnas=fields.Float(string="Horas diurnas", compute="_calcular_lunes", store=True)
    exists_adelanto=fields.Boolean(compute="_get_adelanto",store=True)
    adelanto=fields.Many2one("hr.payslip", "adelanto de sueldo",compute="_get_adelanto",store=True)
    advance_paid=fields.Boolean()
    liquidation_id=fields.Many2one("hr.liquidacion",tracking=True)
    bank_journal_id=fields.Many2one('account.journal',string="Banco",tracking=True)
    account_compromise=fields.Many2one('account.move',string="Compromiso Contable",tracking=True)
    pay_type = fields.Selection(([  ('deposito','DEPOSITO'),
                                    ('cheque','CHEQUE'),
                                    ('pagomovil', 'PAGO MÓVIL'),
                                    ('efectivo', 'EFECTIVO'),
                                    ('mixta', 'MIXTA'),
                                    ]),
                                     string='Forma de Pago',
                                     required=True,default="deposito")
    @api.depends('currency_id_dif','payslip_run_id.tax_today')
    def _tax_today(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
                if record.payslip_run_id.tax_today:
                    record[("tax_today")]=record.payslip_run_id.tax_today
                else:
                    record[("tax_today")] = record.currency_id_dif.rate



                
    @api.depends('employee_id','date_to','type_struct_category')
    def _get_adelanto(self):
        for rec in self:
            if rec.type_struct_category=="normal":
                rec.adelanto=rec.env['hr.payslip'].search([('type_struct_category','=','advance'),('employee_id','=',rec.employee_id.id),('advance_paid','=',False)],order="id desc",limit=1)
                if rec.adelanto:
                    rec.exists_adelanto=True
            

#modificado
    def action_mail_send(self):
        template_id = self.env.ref('eu_dom_payroll.email_template_mass_send')
        template_id.send_mail(self.id, force_send=True)
    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # fill only if the contract as a working schedule linked
        self.ensure_one()
        contract = self.contract_id
        if contract.resource_calendar_id:
            res = self._get_worked_day_lines_values(domain=domain)
            if not check_out_of_contract:
                return res

            # If the contract doesn't cover the whole month, create
            # worked_days lines to adapt the wage accordingly
            out_days, out_hours = 0, 0
            reference_calendar = self._get_out_of_contract_calendar()
            if self.date_from < contract.date_start:
                start = fields.Datetime.to_datetime(self.date_from)
                stop = fields.Datetime.to_datetime(contract.date_start)
                out_time = stop-start
                out_days += out_time.days
                out_hours += out_time.days*24+round(out_time.seconds/3600)
                # out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False)
                # out_days += out_time['days']
                # out_hours += out_time['hours']
            if contract.date_end and contract.date_end < self.date_to:
                start = fields.Datetime.to_datetime(contract.date_end) + relativedelta(days=1)
                stop = fields.Datetime.to_datetime(self.date_to) + relativedelta(days=1,hour=23, minute=59)
                # out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False)
                # out_days += out_time['days']
                # out_hours += out_time['hours']
                out_time = stop-start
                out_days += out_time.days
                out_hours += out_time.days*24+round(out_time.seconds/3600)

            if out_days or out_hours:
                work_entry_type = self.env.ref('hr_payroll.hr_work_entry_type_out_of_contract')
                res.append({
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type.id,
                    'number_of_days': out_days,
                    'number_of_hours': out_hours,
                })
        return res
    def _get_worked_day_lines_values(self, domain=None):
        res=super()._get_worked_day_lines_values()
        #conseguir los que tengan dias feriado
        hours_per_day= self._get_worked_day_lines_hours_per_day()
        domain=self.contract_id._get_work_hours_domain(self.date_from, self.date_to+relativedelta(days=1))
        domain = expression.AND([domain, [
                '|','|','|',
                    ('feriados_libre_laborado_date_start', '=', True),
                    ('feriado_laborado_date_start', '=', True),
                    ('feriados_libre_laborado_date_end', '=', True),
                    ('feriado_laborado_date_end', '=', True)]])
        work_entries = self.env['hr.work.entry'].search(domain).filtered(lambda x: x.work_entry_type_id.code=="WORK100")
        we_holi_and_free=work_entries.filtered(lambda x: x.feriados_libre_laborado_date_start or x.feriados_libre_laborado_date_end)
        we_holi_or_free=work_entries.filtered(lambda x: x.feriado_laborado_date_start or x.feriado_laborado_date_end)
        holidays_calendar= self.env['hr.holidays.per.year'].search([('anno_abo','=',self.date_to.year)],order='id desc', limit=1)

        work_entry_type_holi_and_free=self.env.ref('l10n_ve_payroll.free_holiday_worked')
        work_entry_type_holi_or_free=self.env.ref('l10n_ve_payroll.holiday_worked')
        
        we_holi_and_free_hours=0
        we_holi_or_free_hours=0
        
        # Obtenemos las horas por dia
        # obtenemos las horas feriadas y no feriadas de las entradas
        for we in we_holi_and_free:
            if we.horas_feriadas_totales>0:
                we_holi_and_free_hours+=we.horas_feriadas_totales
            else:
                if we.feriados_libre_laborado_date_start:
                    we_holi_and_free_hours+=we.horas_feriadas_laboradas_date_start
                elif we.feriados_libre_laborado_date_end:
                    we_holi_and_free_hours+=we.horas_feriadas_laboradas_date_end
        for we in we_holi_or_free:
            if we.horas_feriadas_totales>0:
                we_holi_or_free_hours+=we.horas_feriadas_totales
            else:
                if we.feriado_laborado_date_start:
                    we_holi_or_free_hours+=we.horas_feriadas_laboradas_date_start
                elif we.feriado_laborado_date_end:
                    we_holi_or_free_hours+=we.horas_feriadas_laboradas_date_end

        if we_holi_and_free and we_holi_and_free_hours>0:
            days = round(we_holi_and_free_hours / hours_per_day, 5) if hours_per_day else 0
            days_rounded=self._round_days(work_entry_type_holi_and_free, days)
        
            attendance_line = {
                    'sequence': work_entry_type_holi_and_free.sequence,
                    'work_entry_type_id': work_entry_type_holi_and_free,
                    'number_of_days': days_rounded,
                    'number_of_hours': we_holi_and_free_hours,
                }
            res.append(attendance_line)
        if we_holi_or_free and we_holi_or_free_hours>0:
            days = round(we_holi_or_free_hours / hours_per_day, 5) if hours_per_day else 0
            days_rounded=self._round_days(work_entry_type_holi_or_free, days)
        
            attendance_line = {
                    'sequence': work_entry_type_holi_or_free.sequence,
                    'work_entry_type_id': work_entry_type_holi_or_free,
                    'number_of_days': days_rounded,
                    'number_of_hours': we_holi_or_free_hours,
                }
            res.append(attendance_line)

            
        return res
    
    @api.depends('date_to','date_from','employee_id')
    def _calcular_lunes(self):
        for rec in self:
            contador=0
            lunes_sso=0
            martes=0
            miercoles=0
            jueves=0
            viernes=0
            sabado=0
            domingos=0
            formato = "%d/%m/%Y"

            adesde=rec.date_from.year
            mdesde=rec.date_from.month
            ddesde= rec.date_from.day #busca el dia desde
            fechadesde = str(ddesde)+'/'+str(mdesde)+'/'+str(adesde)

            ahasta=rec.date_to.year
            mhasta=rec.date_to.month
            dhasta=rec.date_to.day #busca el final
            monthRange = monthrange(ahasta, mhasta)
            #dhasta = monthRange[1]

            fechahasta = str(dhasta)+'/'+str(mhasta)+'/'+str(ahasta)
            fechadesded = datetime.strptime(fechadesde, formato)
            fechahastad = datetime.strptime(fechahasta, formato)
            
            
            
            new_init_date=False
            new_end_date=False
            if rec.contract_id:
                if rec.contract_id.date_start:
                    new_init_date= rec.contract_id.date_start if rec.date_from<rec.contract_id.date_start else rec.date_from
                
                if rec.contract_id.date_end:
                    new_end_date= rec.date_to if rec.date_to<rec.contract_id.date_end else rec.contract_id.date_end
            if rec.employee_id.in_vacations_since and new_end_date and rec.employee_id.in_vacations_since>new_init_date and rec.employee_id.in_vacations_since<new_end_date and rec.employee_id.in_vacations_till>new_end_date:
                    new_end_date=rec.employee_id.in_vacations_since 
            elif rec.employee_id.in_vacations_till and new_end_date and rec.employee_id.in_vacations_till>new_init_date and rec.employee_id.in_vacations_till<new_end_date:
                    new_init_date=rec.employee_id.in_vacations_till
            elif rec.employee_id.in_vacations_till and rec.employee_id.in_vacations_since and new_end_date and new_init_date and rec.employee_id.in_vacations_till>new_end_date and  rec.employee_id.in_vacations_since<new_init_date:
                new_init_date=False
                new_end_date=False
            else:
                pass
            while fechadesded <= fechahastad:
                
                if datetime.weekday(fechadesded) == 0: #encuentra el dia 0 o lubes
                    contador +=1
                if datetime.weekday(fechadesded) == 0: #encuentra el dia 1 o martes
                    martes +=1
                if datetime.weekday(fechadesded) == 0: #encuentra el dia 2 o miercoles
                    miercoles +=1
                if datetime.weekday(fechadesded) == 0: #encuentra el dia 3 o jueves
                    jueves +=1
                if datetime.weekday(fechadesded) == 0: #encuentra el dia 4 o viernes
                    viernes +=1
                    
                if datetime.weekday(fechadesded) == 5: #encuentra el dia 5 o sabado
                    sabado +=1
                if datetime.weekday(fechadesded) == 6: #encuentra el dia 6 o domingo
                    domingos +=1
                fechadesded = fechadesded + relativedelta(days=1)
            if new_init_date and new_end_date:
                while new_init_date <= new_end_date:
                    if datetime.weekday(new_init_date) == 0:
                        lunes_sso+=1
                    new_init_date = new_init_date + relativedelta(days=1)
            else:
                lunes_sso=contador
            rec.lunes_mes=contador
            rec.lunes_sso=lunes_sso
            rec.sabado_periodo=sabado
            rec.domingo_periodo=domingos
            rec.martes_mes=martes
            rec.miercoles_mes=miercoles
            rec.jueves_mes=jueves
            rec.viernes_mes=viernes
            if rec.date_to==date(rec.date_to.year,rec.date_to.month,monthrange(rec.date_to.year, rec.date_to.month)[1]):
                    
                rec.finmes=True
            else:
                rec.finmes=False
            
            # conseguimos las work_entry

            domain=rec.contract_id._get_work_hours_domain(rec.date_from, rec.date_to)
            
            work_entries = rec.env['hr.work.entry'].search(domain)

            for entries in work_entries.filtered(lambda x: x.work_entry_type_id.code=="WORK100"):
                    duration=entries.duration
                    extra_dia=0
                    extra_noche=0
                    hour=fields.Datetime.context_timestamp(self,entries.date_start).hour
                    while duration:
                        hour+=1
                        if duration>=1:
                            if hour>5 and hour<=19:
                                extra_dia+=1
                            else:
                                extra_noche+=1
                            duration-=1
                        elif duration>0:
                            if hour>=5 and hour<19 and hour>=5 and hour<=19:
                                extra_dia+=duration
                            else:
                                extra_noche+=duration
                            duration=0
                    rec.horas_diurnas+=extra_dia
                    rec.horas_nocturnas+=extra_noche
    def action_refresh_from_work_entries(self):
        #ESTA FUNCION SOBREESCRIBE A LA ANTERIOR CON EL MISMO NOMBRE TENER CUIDADO
        self.ensure_one()
        self._onchange_employee()
        if self.payslip_run_id and self.payslip_run_id.incidence_line_ids:
                        for line in self.payslip_run_id.incidence_line_ids.filtered(lambda x: self.employee_id in x.employee_ids):
                            incidenceline=self.worked_days_line_ids.filtered(lambda x:x.work_entry_type_id.id==line.work_entry_type.id)[:1]
                            if incidenceline:
                                if line.hours_or_days=='hour':
                                    incidenceline.number_of_hours=incidenceline.number_of_hours + line.number_of_unit
                                else:
                                    incidenceline.number_of_days=incidenceline.number_of_days + line.number_of_unit
                                incidenceline.is_incidence=True
                            else:
                                data={
                                    'payslip_id':self.id,
                                    'work_entry_type_id':line.work_entry_type.id,
                                    'name':'INCIDENCIA-'+line.work_entry_type.name,
                                    'display_name':'INCIDENCIA-'+line.work_entry_type.name,
                                    'is_incidence':True
                                }
                                if line.hours_or_days=='hour':
                                    data['number_of_hours']=line.number_of_unit
                                else:
                                    data['number_of_days']=line.number_of_unit
                                self.worked_days_line_ids+=self.env['hr.payslip.worked_days'].create(data)
                        self.has_incidencias=True
        self._calcular_lunes()
        self._actualizar_tabla()
        #self.compute_sheet()
    
        
    @api.onchange('worked_days_line_ids')
    def _actualizar_tabla(self):
        #verificar si en la estructura existe la regla Descanso
        #¿No es mejor solo poner que deba estar enestructura menwsual?
        DDES = self.env['hr.salary.rule'].search([('code', '=', 'DDES'),('struct_id', '=', self.struct_id.id)])
        entry_type_id = self.env['hr.work.entry.type'].search([('code', '=', 'DESCANSO')])
        #No pagados/inasistidos
        if DDES:
            
            for pl in self:

                existe_descanso = False
                new_init_date=pl.date_from
                new_end_date=pl.date_to
                if pl.contract_id:
                    if pl.contract_id.date_start:
                        new_init_date= pl.contract_id.date_start if pl.date_from<pl.contract_id.date_start else pl.date_from
                    
                    if pl.contract_id.date_end:
                        new_end_date= pl.date_to if pl.date_to<pl.contract_id.date_end else pl.contract_id.date_end
                periodo = new_end_date - new_init_date
                periodo = periodo.days + 1
                #Si estoy en el ultimo dia del mes independientemente de que dia caiga, se tomara como 30 dias de trabajo
                diafinal=False
                semanadia=False
                if pl.finmes and periodo>14:
                    periodo= periodo + (30-monthrange(pl.date_to.year, pl.date_to.month)[1])
                    diafinal=monthrange(pl.date_to.year, pl.date_to.month)[1]
                    semanadia=weekday(pl.date_to.year, pl.date_to.month,monthrange(pl.date_to.year, pl.date_to.month)[1])
                
                salario_diario = pl.contract_id.wage / 30
                asistencia = 0 

                if len(pl.worked_days_line_ids)>0 and not existe_descanso:
                    counter_descanso=0
                    ausencias=sum(pl.worked_days_line_ids.filtered(lambda x:x.work_entry_type_id.is_reposo or x.work_entry_type_id.code in ['WORK100']).mapped('number_of_days'))

                    set_workerdays= list(set(pl.contract_id.resource_calendar_id.attendance_ids.filtered(lambda x:x.check_count).mapped('dayofweek')))
                    if diafinal and int(diafinal)>30 and str(semanadia) in set_workerdays:
                        ausencias=ausencias-1
                        to_cut=pl.worked_days_line_ids.filtered(lambda x:x.work_entry_type_id.is_reposo or x.work_entry_type_id.code in ['WORK100'])[:1]
                        if to_cut:
                            to_cut.number_of_days=to_cut.number_of_days-1

                    for i in range(0,periodo):
                        is_weekday=weekday((new_init_date+relativedelta(days=i)).year, (new_init_date+relativedelta(days=i)).month, (new_init_date+relativedelta(days=i)).day)
                        if str(is_weekday) not in set_workerdays:
                            counter_descanso+=1

                    # entradas_dias=pl.worked_days_line_ids.filtered(lambda w: w.work_entry_type_id.code in ['WORK100','LEAVE90'])
                    # minus=0
                    # if entradas_dias:
                    #     minus=sum(entradas_dias.mapped('number_of_days'))
                    if counter_descanso>0 :

                        number_of_days=periodo -ausencias if periodo -ausencias<=counter_descanso else counter_descanso
                        
                        if number_of_days>0 and not pl.worked_days_line_ids.filtered(lambda x:x.work_entry_type_id==entry_type_id):
                            pl.worked_days_line_ids = [(0, 0,  {
                            'amount': (salario_diario * number_of_days),
                            'contract_id': pl.contract_id.id,
                            'sequence': entry_type_id.sequence,
                            'work_entry_type_id': entry_type_id.id,
                            'name': 'Días Descanso',
                            'number_of_days':  number_of_days,
                        })]
                        elif number_of_days>0:
                                pl.worked_days_line_ids.filtered(lambda x:x.work_entry_type_id==entry_type_id)[:1].number_of_days=number_of_days
                        else:
                            pl.worked_days_line_ids.filtered(lambda x:x.work_entry_type_id==entry_type_id)[:1].unlink()
# periodo - asistencia if pl.finmes else
    @api.depends('sal_mensual')
    def _sal_diario(self):
        for record in self:
            record["sal_diario"] = round(record.sal_mensual / 30,4)

    @api.depends('sal_mensual_usd')
    def _sal_diario_usd(self):
        for record in self:
            record["sal_diario_usd"] = round(record.sal_mensual_usd / 30,4)

    lunes_mes = fields.Integer(store=True, compute='_calcular_lunes', string="Cantidad de lunes en el mes",tracking=True)
    lunes_sso = fields.Integer(store=True, compute='_calcular_lunes', string="Cantidad de lunes en sso",tracking=True)

    martes_mes = fields.Integer(store=True, compute='_calcular_lunes', string="Cantidad de martes en el mes",tracking=True)
    miercoles_mes = fields.Integer(store=True, compute='_calcular_lunes', string="Cantidad de miercoles en el mes",tracking=True)
    jueves_mes=fields.Integer(store=True, compute='_calcular_lunes', string="Cantidad de jueves en el mes",tracking=True)
    viernes_mes = fields.Integer(store=True, compute='_calcular_lunes', string="Cantidad de viernes en el mes",tracking=True)
    sabado_periodo = fields.Integer(store=True, compute='_calcular_lunes', string="N° de Sabados",tracking=True)
    domingo_periodo = fields.Integer(store=True, compute='_calcular_lunes', string="N° de Domingos",tracking=True)
    sal_mensual = fields.Float(store=True, readonly=True, related='contract_id.wage', string="Salario Mensual (Bs)",tracking=True)
    sal_mensual_usd = fields.Float(store=True, readonly=True, related='contract_id.amount_total_usd',
                                   string="Salario Mensual (USD)")

    sal_diario = fields.Float(store=True,tracking=True, readonly=True, compute="_sal_diario", string="Salario Diario (Bs)")
    sal_diario_usd = fields.Float(store=True, readonly=True,tracking=True, compute="_sal_diario_usd", string="Salario Diario (USD)")

    def action_payslip_cancel(self):
        if self.env.user.has_group("hr_payroll.group_hr_payroll_user"):
            self.state="draft"
        res= super().action_payslip_cancel()
        if self.account_compromise:
            self.account_compromise.button_cancel()
        return res

    def action_payslip_done(self):
        # if self.filtered(lambda x: x.payslip_run_id):
            # for run in self.filtered(lambda x: x.payslip_run_id).mapped('payslip_run_id') :
                # if not run._are_payslips_ready():
                #     raise UserError("Nóminas con lote deben confirmarse desde su lote o tener el mismo en estado 'hecho'")
        super(HRPayslip, self).action_payslip_done()

        for rec in self:
            if rec.exists_adelanto and rec.adelanto:
                rec.adelanto.advance_paid=True
            if rec.is_vacation:
                rec.employee_id.in_vacations_since=rec.date_from
                rec.employee_id.in_vacations_till=rec.date_to +relativedelta(days =1)
                rec.move_id.date=rec.date_from

            if rec.struct_id.auto_post and rec.move_id.state!='posted':
                rec.move_id.action_post()
            rec.message_post(body=f"Creada Entrada en Borrador {rec.move_id.name}")
    


    @api.depends('date_from','date_to')
    @api.constrains("employee_id")
    def _payslip_duplicated_by_date(self):
        for rec in self:
            if self.env['hr.payslip'].search([('state','not in',['cancel']),('employee_id','=',rec.employee_id.id),('date_from','=',rec.date_from),('date_to','=',rec.date_to),('company_id','=',rec.env.company.id),('id','!=',rec.id),('struct_id','=',rec.struct_id.id)]):
                raise UserError("Ya existe una nómina para este empleado en este periodo, si no la visualiza. haga click en 'Todas las nominas' ")
    
    def compute_sheet(self,adddays=0,colective=False):
        for rec in self:
            # rec.action_refresh_from_work_entries()
            rec._onchange_is_vacation(adddays,colective)
        res = super(HRPayslip, self).compute_sheet()
        return res


    """Hey hey Ñeri here, apartir de aca ira la seccion de Vacaciones
    Lo que debera hacer esta seccion es crear la logica para que cuando
    se este en vacaciones tome automaticamente la fecha final en la que saldra el trabajador
    """

    def _get_calendario_feriado(self):
        for rec in self:
            thisdateyear=rec.date_from.year
            thisyear=TODAY.year
            if self.env['hr.holidays.per.year'].search([('anno_abo','=',thisdateyear)],order='id desc', limit=1):
                return self.env['hr.holidays.per.year'].search([('anno_abo','=',thisdateyear)],order='id desc', limit=1)
            else:
                return self.env['hr.holidays.per.year'].search([('anno_abo','=',thisyear)],order='id desc', limit=1)


    is_vacation=fields.Boolean(string="Vacacion")

    dias_vacaciones=fields.Integer(related="company_id.dias_vac_base",tracking=True)
    dias_bonificaciones=fields.Integer( compute="_get_bonification_days",store=True,tracking=True)
    dias_feriados=fields.Integer(store=True,tracking=True,compute="_onchange_is_vacation")
    anno_vacaciones_designado=fields.Integer(string="Vacaciones del año",default=TODAY.year)
    
    @api.depends('anno_vacaciones_designado','employee_id')
    def _get_bonification_days(self):
        for rec in self:
            anos=rec.anno_vacaciones_designado-(rec.employee_id.fecha_inicio.year if rec.employee_id.fecha_inicio else 0)
            if anos>=2:
                rec.dias_bonificaciones=1+(anos-2)
            else:
                rec.dias_bonificaciones=0
    @api.constrains("anno_vacaciones_designado")
    def _cosntrain_anno_vacacion_designate(self):
        for rec in self:
            if rec.liquidation_id:
                pass
            elif rec.employee_id.fecha_inicio and rec.is_vacation and rec.anno_vacaciones_designado<rec.employee_id.fecha_inicio.year:
                raise UserError(f"Este no es un año valido para las vacaciones del empleado {rec.employee_id.name}")
            else:
                pass

    
    
    
    @api.onchange('date_from','is_vacation','anno_vacaciones_designado')
    def _onchange_is_vacation(self,days_preset=0,colective=False):
        for rec in self:
            total=0
            contador=0
            date_fixed=False
            date_to= rec.date_from
            counter_festivities=0
            calendario=rec._get_calendario_feriado()
            if rec.is_vacation and rec.employee_id:
                
                if days_preset and colective:
                    dias_vacacionales=days_preset
                    date_fixed=date_to+relativedelta(days = days_preset)
                elif days_preset:
                    dias_vacacionales=days_preset
                else:
                    dias_vacacionales= rec.dias_vacaciones+rec.dias_bonificaciones
                
                while total<dias_vacacionales:
                    if date_to in calendario.holidays_lines_ids.mapped("fecha") and date_to.weekday() not in [5,6]:
                        counter_festivities+=1
                    elif date_to.weekday()  in [5,6]:
                        pass
                    else:
                        total+=1
                    date_to= date_to+relativedelta(days =1)
                if date_fixed:   
                    rec.date_to = date_fixed
                else:
                    rec.date_to = date_to-relativedelta(days =1)
                rec._calcular_lunes()
                counter_festivities+=contador
                rec.dias_feriados=rec.sabado_periodo+rec.domingo_periodo+counter_festivities
            elif rec.employee_id:
                periodo = rec.date_from - rec.date_to
                periodo = periodo.days + 1
                while total<periodo:
                    if date_to in calendario.holidays_lines_ids.mapped("fecha") and date_to.weekday() not in [5,6]:
                        counter_festivities+=1
                    date_to= date_to+relativedelta(days =1)
                    total+=1
                rec.dias_feriados=counter_festivities

    #revisa si la persona tiene vacaciones para facturar
    @api.constrains('employee_id')
    def _constrain_vacaciones(self):
        for rec in self:
            if rec.is_vacation and not rec.liquidation_id:
                vacaciones=rec.env['hr.payslip'].search([('state','not in',['cancel']),('employee_id','=',rec.employee_id.id),('is_vacation','=',True),('id','!=',rec.id)])
                if len(vacaciones)>rec.employee_id.vacaciones_total:
                    raise UserError("Este individuo ya a usado todas sus vacaciones disponibles")
                if vacaciones.filtered(lambda x: x.id !=rec.id and x.anno_vacaciones_designado==rec.anno_vacaciones_designado):
                    raise UserError("Ya este trabajador "+rec.employee_id.name+" presenta vacaciones para el año "+str(rec.anno_vacaciones_designado))

    #Data de lote para text

    monto=fields.Float(compute="_compute_monto_a_pagar")

    @api.depends('line_ids')
    def _compute_monto_a_pagar(self):
        for rec in self:
            rec.monto=sum(rec.line_ids.filtered(lambda x: x.category_id.code not in ["DED","COMP"]).mapped("total"))-sum(rec.line_ids.filtered(lambda x: x.category_id.code =="DED").mapped("total"))
    

    """WE CONTINUE! PRESSING ONWARD ON OUR DREADFUL JOURNEY THROUGH THE ABYSS 
    Ahora incluiremos calculos para obtener las horas extra tanto diurnas como nocturnas"""
    @api.depends('contract_id','employee_id','date_from','date_to','worked_days_line_ids')
    def _compute_extra_hours(self):
        for rec in self:
            rec.hours_exday=0
            rec.hours_exnight=0
            work_entries=self.env['hr.work.entry'].search(rec.contract_id._get_work_hours_domain(rec.date_from-relativedelta(days=1),rec.date_to+relativedelta(days=1),domain=None,inside=True))
            work_entries=work_entries.filtered(lambda x: fields.Datetime.context_timestamp(self,x.date_start).date()>= rec.date_from and fields.Datetime.context_timestamp(self,x.date_stop).date()<=rec.date_to)
            if work_entries:
                
                work_scheduled_hours=rec.contract_id.resource_calendar_id.hours_per_day
                for entries in work_entries.filtered(lambda x: x.work_entry_type_id.code=="WORK300"):
                    duration=entries.duration
                    extra_dia=0
                    extra_noche=0
                    hour=fields.Datetime.context_timestamp(self,entries.date_start).hour
                    while duration:
                        hour+=1
                        if duration>=1:
                            if hour>5 and hour<=19:
                                extra_dia+=1
                            else:
                                extra_noche+=1
                            duration-=1
                        elif duration>0:
                            if hour>=5 and hour<=19:
                                extra_dia+=duration
                            else:
                                extra_noche+=duration
                            duration=0
                        else:
                            duration=0
                    if extra_noche>=rec.env.company.horas_change_noche:
                        rec.hours_exday+=0
                        rec.hours_exnight+= extra_dia + extra_noche
                    else:
                        rec.hours_exday+=extra_dia
                        rec.hours_exnight+=extra_noche
    

    # aqui colocaremos flags para utilidades

    is_utility=fields.Boolean(string="Es utilidad")
    is_anihilation=fields.Boolean("Es Liquidación")
    brute_sum=fields.Float(compute="_get_full_sum",string="Total sin Deduccion",tracking=True,store=True)
    total_sum=fields.Float(compute="_get_full_sum",string="Total a pagar",tracking=True,store=True)
    total_costo=fields.Float(compute="_get_full_sum",string="Total a Costear",tracking=True,store=True)
    @api.depends('line_ids','line_ids.total')
    def _get_full_sum(self):
        for rec in self:
            lines = rec.line_ids.filtered(lambda line: line.category_id.code not in ['DED','COMP','PROV'] and line.salary_rule_id.appears_on_payslip)
            minus= rec.line_ids.filtered(lambda line: line.category_id.code == 'DED' and line.salary_rule_id.appears_on_payslip)
            full= rec.line_ids.filtered(lambda line: line.salary_rule_id.appears_on_payslip)
            
            rec.brute_sum = round(sum([line.total for line in lines]),4)

            rec.total_sum = round(sum([line.total for line in lines])-sum([line.total for line in minus]),4)
            rec.total_costo = round(sum([line.total for line in full]),4)

    salario_promedio=fields.Float("Salario Prom. diario")
    @api.onchange('employee_id','date_from','date_to')
    def _onchange_salario_promedio(self):
        for rec in self:
            if rec.date_from:
                begintime=rec.date_from -relativedelta(months=3)
            else:
                begintime=rec.date_to
            nominas=rec.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),('date_from', '>=', begintime),('date_to', '<=', rec.date_from),('is_vacation','=',False),('is_anihilation','=',False),('is_utility','=',False),('type_struct_category','in',['normal','especial'])])
            sal=sum(sum(y.total for y in x.line_ids.filtered(lambda line: line.category_id.code == 'BASIC')) for x in nominas)
            
            rec.salario_promedio=sal/90 if sal>0 else 0

    comprometida=fields.Boolean("con compromiso de pago")
    
    # def return_receipts(self):
    #     return self.env.ref('l10n_ve_payroll.report_payslip_custom').report_action(self)

    # def massive_receipt_queue(self):
    #     chunk = lambda l, n: [l[i:i + n] for i in range(0, len(l), n)]
    #     self.env.ref('l10n_ve_payroll.report_payslip_custom').delayable().report_action(self)
    #     delayables=self.delayable()
    #     cienes=chunk(delayables,100)

    #     for c in cienes:
    #         c.return_receipts()

    
    def regenerate_account_move(self):
        for rec in self:
            if rec.move_id:
                if rec.move_id.state=="posted":
                    rec.move_id.button_draft()
                    rec.move_id.button_cancel()
                    rec.move_id.message_post(body=f"Este movimiento fue cancelado por regeneración de asiento de nómina {rec.number}")
                    rec.move_id=False
                    rec.action_payslip_draft()
                    rec.compute_sheet()
                    rec.action_payslip_done()
                elif rec.move_id.state=="cancel":
                    rec.move_id=False
                    rec.action_payslip_draft()
                    rec.compute_sheet()
                    rec.action_payslip_done()
                else:
                    rec.move_id.button_cancel()
                    rec.move_id.message_post(body=f"Este movimiento fue cancelado por regeneración de asiento de nómina {rec.number}")
                    rec.move_id=False
                    rec.action_payslip_draft()
                    rec.compute_sheet()
                    rec.action_payslip_done()
            else:
                    rec.action_payslip_draft()
                    rec.compute_sheet()
                    rec.action_payslip_done()
            if rec.account_compromise:
                if rec.account_compromise.state=="posted":
                    rec.account_compromise.button_draft()
                    rec.account_compromise.button_cancel()
                    rec.account_compromise.message_post(body=f"Este movimiento fue cancelado por regeneración de asiento de nómina {rec.number}")
                    rec.account_compromise=False
                    rec.compute_sheet()
                elif rec.account_compromise.state=="cancel":
                    rec.account_compromise=False
                    rec.compute_sheet()
                else:
                    rec.account_compromise.button_cancel()
                    rec.account_compromise.message_post(body=f"Este movimiento fue cancelado por regeneración de asiento de nómina {rec.number}")
                    rec.account_compromise=False
                    rec.compute_sheet()
