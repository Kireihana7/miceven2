# -*- coding: utf-8 -*-

import re
from unicodedata import category
import xlrd
import base64
import random
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields,api
from datetime import datetime, timedelta,date
from calendar import monthrange

class HRPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ["hr.payslip.run",'mail.thread', 'mail.activity.mixin']
    name = fields.Char(required=True,readonly=False)
    block_sec=fields.Boolean(string="adelantada secuencia de txt",tracking=True)
    txt_linea_valuefirst=fields.Char()
    txt_linea_valuelast=fields.Char()
    txt_cabecera_value=fields.Char()
    job_id_filter=fields.Many2one('hr.job',"Cargo",tracking=True)
    vacation=fields.Boolean()
    state=fields.Selection(selection_add=[('cancel', 'Cancelado')],ondelete={'cancel':'set default'},default="draft",tracking=True)
    has_incidencias=fields.Boolean(string="Tiene incidencias",tracking=True,default=True)
    is_utility=fields.Boolean()
    is_vacation=fields.Selection([('yes','Individuales'),('no','Colectivas')],string="Tipo de vacaciones",tracking=True)
    ignorate_on_vacations=fields.Boolean("Ignorar en vacaciones",tracking=True)
    search_with_vacations=fields.Boolean("Solo empleados con vacaciones",tracking=True)
    department_id_filter=fields.Many2one('hr.department',"Departamento",tracking=True)
    category_id_filter=fields.Many2one('hr.employee.category',string="Categoria Empleado",tracking=True)
    use_alternal_nomina_txt=fields.Boolean('Usar para txt nomina')
    incidence_line_ids=fields.Many2many('incidence.line',string="Incidencias",tracking=True)
#region txtGENERATOR
    ''' Hey! Ñeri here...again, apartir de ahora vendra info necesaria para el la formacion del txt de las nominas,
    vulgarmente conocidas como edi'''
    banco = fields.Many2one('res.bank', string="Banco asociado a las cuotas",tracking=True)
    journal_id = fields.Many2one('account.journal', "Diario asociado",tracking=True)
    bank_code = fields.Selection(
        related="journal_id.txt_payment", 
        string="Banco asociado al diario", 
        readonly=True,tracking=True
    )
    len_cuotas = fields.Char(compute="_compute_len_cuotas",string="número de nóminas",store=True)
    company_rif = fields.Char(compute="_compute_company_rif")
    mercantil_number = fields.Integer()
    currency_id_dif = fields.Many2one("res.currency", 
        string="Referencia en Divisa",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),)
    tax_today= fields.Float(readonly=False, compute="_tax_today",store=True, string="Tasa del Día",tracking=True) 
    
    date_end=fields.Date(tracking=True)
    date_start=fields.Date(tracking=True)
    @api.onchange('has_incidencias')
    def onchange_incidencia(self):
        for rec in self:
            if not rec.has_incidencias:
                rec.incidence_line_ids=False
    def get_all_available_incidences(self):
        for rec in self:
            domain=[('fecha_ini','=',rec.date_start),('fecha_fin','=',rec.date_end),('category_id','=',rec.category_id_filter.id)]
            incidencias=self.env['incidence.line'].search(domain)
            if not incidencias:
                raise UserError("No tiene incidencias para las caracteristicas de su lote")
            else:
                rec.incidence_line_ids=incidencias
    def cancel_all(self):
        for rec in self:
            if rec.slip_ids.filtered(lambda x:x.state =='done'):
                raise UserError("No puede cancelar con nominas hechas")
            for slip in rec.slip_ids:
                slip.action_payslip_cancel()
            rec.state="cancel"
    def pass_seq_numbers(self):
        for rec in self:
            rec.txt_cabecera_value=rec.journal_id.txt_sec_for_header._get_number_next_actual()
            rec.txt_linea_valuefirst=self.env['ir.sequence'].next_by_code(rec.journal_id.txt_sec_for_header.code)
            #  for times in rec.slip_ids[1:]:
            #     rec.txt_linea_valuelast=self.env['ir.sequence'].next_by_code(rec.journal_id.txt_sec_for_lines.code)
            rec.block_sec=True

    def _get_available_contracts_domain(self):
        
        for run in self:
            domain=[('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]
            if run.department_id_filter:
                domain.append(('department_id','=',run.department_id_filter.id))
            if run.category_id_filter:
                domain.append(('category_ids','=',run.category_id_filter.id))
            if run.job_id_filter:
                domain.append(('contract_id.job_id','=',run.job_id_filter.id))
            if run.struct_id and (run.check_special_struct==False and run.vacation==False):
                domain.append(('contract_id.struct_id','=',run.struct_id.id))
            if run.ignorate_on_vacations:
                domain.append(('in_vacations_till','=',False))
            if run.search_with_vacations:
                domain.append(('has_vacations_loose','=',True))
            return domain

    def get_employees(self):
        for run in self:
        # YTI check dates too
            if run.search_with_vacations:
                return self.env['hr.employee'].search(run._get_available_contracts_domain()).filtered(lambda x:x.has_vacations_loose)
            else:
                return self.env['hr.employee'].search(run._get_available_contracts_domain())


    @api.depends('currency_id_dif')
    def _tax_today(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
                record[("tax_today")] = record.currency_id_dif.rate
    def compute_all_payslips(self):
        if len(self.slip_ids) < 1:
            raise ValidationError(u"Debe generar alguna nómina primero.")
        # self.assign_worked_hours()
        if self.vacation and self.is_vacation=="no":
            for payslip in self.slip_ids.filtered(lambda slip: slip.state != 'done'):
                
                payslip.action_refresh_from_work_entries()
                payslip.compute_sheet((self.date_end- self.date_start).days+1,True)
                
        else:
            for payslip in self.slip_ids.filtered(lambda slip: slip.state != 'done'):
                
                payslip.action_refresh_from_work_entries()
                payslip.compute_sheet()
                
 #region Computes
    # Dominio y definicion de las cuotas que seran comprobadas por el edi
    @api.depends("company_id")
    def _compute_company_rif(self):
        for rec in self:
            rec.company_rif = rec.company_id.rif.replace("-", "") if rec.company_id.rif else ''

    @api.depends("slip_ids")
    def _compute_len_cuotas(self):
        for rec in self:
            rec.len_cuotas = str(len(rec.slip_ids))
    #endregion

    def action_print_payslip(self):
        for rec in self:
            if not rec.slip_ids.filtered(lambda x: x.state=='done'):
                raise UserError ("no hay nominas confirmadas")
            else:
        # self.env.ref('l10n_ve_payroll.report_payslip_custom').report_action(self)
                return {
            'name': 'Payslip',
            'type': 'ir.actions.act_url',
            'url': '/print/payslips?list_ids=%(list_ids)s' % {'list_ids': ','.join(str(x) for x in rec.slip_ids.ids)},
        }


    def get_txt(self, content, bank):
        
        return { 
            "content"   : base64.encodebytes(bytes("\n".join(content) if type(content)==type(['Array','type']) else content, 'utf-8')),
            "bank"      : bank.upper(),
            "date"      : self.date_start.strftime("%m/%d/%y")
        }

    def get_txt_by_bank(self,bank):
        METHODS = {
            "0108": self.txt_provincial,
            "0114": self.txt_caribe,
            "0116": self.txt_bod,
            "0134": self.txt_banesco,
            "0105": self.txt_mercantil,
            "0104": self.txt_venezolano_credito,
            "0102": self.txt_venezuela,
        }

        if not bank.bic in METHODS:
            # raise UserError("El banco no está registrado, contacte con el administrador de su sistema")
            return False
        
        return METHODS.get(f'{bank.bic}',False)() #quitaremos esto debido a que no sera utilizado de momento
    #endregion

    #region Bancos

    #region Helpers
    get_fecha = staticmethod(lambda f = "%Y%m%d": date.today().strftime(f))
        
    convert = lambda self, amount: \
        amount * self.manual_currency_exchange_rate if self.currency_id.name == "USD" \
            else amount / self.manual_currency_exchange_rate

    format_monto = lambda self, monto: f"{monto:.2f}".replace(".", "")

    get_total_monto = lambda self: self.format_monto(sum(self.slip_ids.mapped("monto")))

    get_random = staticmethod(lambda: str(random())[2:6])

    #endregion

    #region Header
    def header_mercantil(self):
        FECHA = self.get_fecha()

        self.mercantil_number = self.get_random()

        return "".join([
            "1BAMRVECA    C1",
            (FECHA + str(self.mercantil_number)).ljust(15),
            "DOMIC".zfill(11),
            "J0" + self.company_rif[1:],
            str(len(set(self.slip_ids.mapped("employee_id.id")))).zfill(8),
            "".join([
                self.get_total_monto().zfill(17), 
                FECHA, 
                self.journal_id.bank_account_id.acc_number
            ]),
            "".zfill(102), 
            " " * 48
        ])

    def header_banesco(self):
        FECHA = self.get_fecha()

        return "\n".join(
            map("".join, [
                [
                    "HDRBANESCO".ljust(18),
                    "ED  95BPAYMULP",
                ],
                [
                    "01SCV".ljust(37) + "9  ",
                    (" " * 23).join(map(lambda e: "".join(e), zip([FECHA] * 2, ["1129", "112612"]))),
                ],
                [
                    "0200000001".ljust(32),
                    self.company_rif.ljust(17),
                    self.company_id.name[:35].ljust(35),
                    (self.get_total_monto() + "VES").zfill(18),
                    " " + self.journal_id.bank_account_id.acc_number,
                    "   ".join(["BANSVECA", FECHA + "CB"]).rjust(36)
                ]
            ])
        )

    def header_bod(self):
        return "".join([
            "01" + self.get_fecha("%d%m%Y"),
            str(len(self.slip_ids)).zfill(5),
            self.get_total_monto().zfill(15),
            "180563386CR".zfill(15),
            "0" * 16
        ])
    
    def header_venezolano_credito(self):
        FECHA = self.get_fecha()

        return "".join([
            ("CO0001501000" + FECHA + "0955" + "115".zfill(15)) + (" " * 33),
            (("0" * 7) + self.company_id.name).ljust(78),
            "".join([
                FECHA,
                self.len_cuotas.zfill(9), 
                self.get_total_monto().zfill(17), 
                "1".zfill(11),
                FECHA.zfill(17),
                self.company_rif,
            ]),
            (" " * 10) + "0104" + (" " * 8),
            self.journal_id.bank_account_id.acc_number
        ])
    
    def header_venezuela(self):
        today = str(date.today()).replace("-", "/")
        return "".join([
            "01" + self.company_rif.replace("-", ""),
            str(len(self.slips_filtered())).zfill(10),
            self.get_total_monto().zfill(13),
            today,
            self.get_random().zfill(12),
            self.get_random().zfill(20),
            today.zfill(50),
            str(date.today() + timedelta(days=3)).replace("-", "/"),
        ])
 
    slips_filtered = lambda self: self.slip_ids.filtered(lambda c: c.state in ["verify",'done'])
  

    def filter_by_bank(self,slip_ids,bank):
        return slip_ids.filtered(lambda x: x.employee_id.bank_account_id_emp_2.bic==bank)
    def pagada_slip(self, ad):
        for slip in self.slip_ids.search([('id', 'in', ad)]):
            slip.state = "done"

    def txt_mercantil(self,bank=None):
        lines = []

        if self.use_alternal_nomina_txt:
            raise UserError("Aun no se a añadido esta txt nómina para este banco")
        lines.append(self.header_mercantil())

        for slip in (self.filter_by_bank(self.slips_filtered,bank) if bank else self.slips_filtered()) :
            if slip.employee_id.has_autorized:
                cedula_v = slip.employee_id.ci_autorizate
                cuenta=slip.employee_id.account_number_autorizate
            else:
                cedula = slip.employee_id.identification_id_2
                cuenta=slip.employee_id.account_number_2
                cedula_v = "V" + cedula.zfill(10)

            lines.append(
                "".join([
                    "".join([
                       "2" + cedula_v,
                       cuenta,
                    ]).ljust(43),
                    cedula_v.ljust(25),
                    self.format_monto(slip.monto).zfill(17).ljust(47),
                    cedula_v.ljust(17),
                    "".join([
                        str(slip.id).zfill(16),
                        self.get_fecha() + "".zfill(4),
                    ]).ljust(58),
                    "".join([
                        str(slip.id).zfill(13),
                        self.get_fecha() * 2,
                    ])
                ])
            )

        return self.get_txt(lines, "mercantil")

    def txt_bod(self,bank=None):
        lines = []

        lines.append(self.header_bod())

        for slip in (self.filter_by_bank(self.slips_filtered,bank) if bank else self.slips_filtered()) :
            if slip.employee_id.has_autorized:
                cedula_v = slip.employee_id.ci_autorizate
                cuenta=slip.employee_id.account_number_autorizate
            else:
                cedula = slip.employee_id.identification_id_2
                cuenta=slip.employee_id.account_number_2
                cedula_v = "V" + cedula.zfill(10)
            lines.append(
                "".join([
                    "02DB0" + cuenta,
                    str(slip.id).zfill(15),
                    self.format_monto(slip.monto).zfill(15),
                    self.get_fecha("%d%m%y")
                ])
            )

        return self.get_txt(lines, "bod")

    def txt_venezolano_credito(self,bank=None):
        lines = []

        FECHA = self.get_fecha()
        if self.use_alternal_nomina_txt:
            raise UserError("Aun no se a añadido esta txt nómina para este banco")
        FECHA_LINE = ("CO0001501000" + FECHA + "0955" + "115".zfill(15)) + (" " * 33)

        lines.append(self.header_venezolano_credito())

        for slip in (self.filter_by_bank(self.slips_filtered,bank) if bank else self.slips_filtered()) :
            if slip.employee_id.has_autorized:
                cedula_v = slip.employee_id.ci_autorizate
                cuenta=slip.employee_id.account_number_autorizate
                nombre=slip.employee_id.name_autorizate
            else:
                cedula = slip.employee_id.identification_id_2
                cuenta=slip.employee_id.account_number_2
                cedula_v = slip.employee_id.rif.replace("-", "")
                nombre=slip.employee_id.name
            lines.append("".join([
                FECHA_LINE,
                "".join([
                    "DBDB0104".zfill(16),
                    cuenta,
                ]).ljust(51),
                str(slip.id).zfill(15).ljust(35),
                (self.format_monto(slip.monto).zfill(16) + "104".zfill(11)).ljust(35),
                cedula_v.ljust(20),
                nombre.ljust(98),
                FECHA + "N".zfill(9),
                str(self.id).zfill(7).rjust(29)
            ]))

        lines.append(("" * 33).join([
            FECHA_LINE,
            self.get_total_monto().zfill(24) + str(len(self.slip_ids)).zfill(10)
        ]))

        return self.get_txt(lines, "venezolano_credito")

    def txt_banesco(self,bank=None):
        
        rs=''
        content = ''
        
        date = datetime.now().strftime("%d/%m/%Y%H%M%S").replace("/", "")
        for e in self.slip_ids.filtered(lambda x:x.state!='cancel').mapped('employee_id'):
            if not e.account_number_2 and not e.has_autorized:
                raise UserError(f"El empleado {e.name} no tiene cuenta, para generar un txt, se necesita una cuenta. coloquela.")
            if  e.has_autorized and not e.account_number_autorizate:
                raise UserError(f"El empleado {e.name} indica un autorizado pero este no tiene cuenta, para generar un txt, se necesita una cuenta. coloquela.")
        cuentas_empleados = False if len(self.slip_ids.filtered(lambda x:x.state!='cancel').mapped('employee_id').filtered(lambda line: not line.has_autorized and str(line.account_number_2[:4]) != '0134')) > 0 else True
        cuentas_autorizados = False if len(self.slip_ids.filtered(lambda x:x.state!='cancel').mapped('employee_id').filtered(lambda line:  line.has_autorized and str(line.account_number_autorizate[:4]) != '0134')) > 0 else True

        if cuentas_empleados and cuentas_autorizados:
            nombre_archivo = 'BPROV-BANES'+ ''+ str(date)+'.txt'    
        else:
            nombre_archivo = 'BPRO-BANES'+ ''+ str(date)+'.txt'
        
        count_batch = self.env['hr.payslip.run'].search_count([('journal_id','=',self.journal_id.id),('id','!=',self.id),('date_start','=',self.date_start)]) + 1
        # la cabecera
        nom = 'HDRBANESCO        ED  95BPAYMULP'
        content += '%s\n'%(
            nom.ljust(32),
        )
        # segunda linea
        if self.use_alternal_nomina_txt:
            est = '01SAL'
        else:
            est = '01SCV'
        space = " "
        num = '9'
        # randomUpperLetter = chr(random.randint(ord('A'), ord('Z')))
        # randomUpperLetter2 = chr(random.randint(ord('A'), ord('Z')))
        randomUpperdigit = chr(random.randint(ord('0'), ord('9')))
        randomUpperdigit2 = chr(random.randint(ord('0'), ord('9')))
        letters = str(randomUpperdigit)+ str(randomUpperdigit2)
        date = datetime.now().strftime("%d%m%y").replace("/","")
        if self.txt_cabecera_value:
            userdate = self.txt_cabecera_value
        else:
            userdate = letters + str(date)+ str(count_batch)
        fecha = datetime.now().strftime("%Y%m%d%H%M%S").replace("/","")
        
        # fecha = header.date.strftime("%Y%m%d%H%M%S").replace("/", "")
        content += '%s%s%s%s%s%s%s\n'%(
            est.ljust(5),
            space.ljust(32),
            num.ljust(1),
            space.ljust(2),
            userdate.ljust(9),
            space.ljust(26),
            fecha.ljust(14)
        )
        num="02"
        if self.txt_linea_valuefirst:
            num_reg = self.txt_linea_valuefirst
        else:
            num_reg = str(self.id)
        num_reg2 = ''.join([i for i in num_reg if not i.isalpha()])
        num_restante = num_reg2[-8:].zfill(8)
        space = " "
        primera_letra_rif = self.company_id.rif[0] if self.company_id.rif else ''
        restante_rif= self.company_id.rif[2:] if self.company_id.rif else ''
        nom_empresa = (self.company_id.name).replace(",","").replace(".","").replace("'","")
        replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
        new_name = re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], nom_empresa)
        amount_cal = "{0:.2f}".format(sum(self.slip_ids.filtered(lambda x:x.state!='cancel').mapped('total_sum')))
        amount_cal = rs.join(str(amount_cal).split('.'))
        amount_cal = amount_cal.zfill(15)
        ves = 'VES'
        banesco = 'BANESCO'
        fecha_pago = datetime.now().strftime('%Y%m%d').replace("/","")
        
        content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
            num.ljust(2),
            num_restante.ljust(8).zfill(8),
            space.ljust(22),
            primera_letra_rif.ljust(1),
            restante_rif.ljust(9),
            space.ljust(7),
            new_name[:32].ljust(32),
            space.ljust(3),
            amount_cal.ljust(15),
            ves.ljust(3),
            space,
            self.journal_id.bank_account_id.acc_number.ljust(20),
            space.ljust(14),
            banesco.ljust(7),
            space.ljust(4),
            fecha_pago.ljust(8),
        )
        for wh in self.slip_ids.filtered(lambda x:x.state!='cancel'):
                if wh.employee_id.has_autorized:
                    cedula_v = wh.employee_id.ci_autorizate
                    cuenta=wh.employee_id.account_number_autorizate
                    nombre=wh.employee_id.name_autorizate
                else:
                    cedula = wh.employee_id.identification_id_2
                    cuenta=wh.employee_id.account_number_2
                    cedula_v = wh.employee_id.identification_id_2.replace("-", "")
                    nombre=wh.employee_id.name
                if not self.journal_id.bank_account_id.acc_number:
                    raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                if not  cuenta:
                    raise UserError('Hay empleados sin cuenta configurada')
                    ############## DEBITO###########
                
                ########## credito ##############
                if cedula_v:
                    primera_letra_rif_partner = cedula_v[0] if cedula_v and cedula_v[0].upper() in ['V','E'] else 'V'
                    cedularestante=cedula_v[1:].replace('-','')
                    restante_rif= cedula_v[1:] if cedularestante[0].upper() in ['V','E'] else cedularestante
                else:
                    primera_letra_rif_partner = ''
                    restante_rif= ''
                restante_rif  = restante_rif
                num2="03"
                num_reg = (wh.number).replace("/","").replace(".","").replace("-","")
                num_reg2 = ''.join([i for i in num_reg if not i.isalpha()])
                num_restante = num_reg2[-8:].zfill(8)
                space = " "
                amount_cal = "{0:.2f}".format(wh.total_sum)
                amount_cal = rs.join(str(amount_cal).split('.'))
                amount_cal = amount_cal.zfill(15)
                ves1 = 'VES'
                primeros_4_num_account = cuenta[:4]
                if primeros_4_num_account == '0134':
                    last_num = '42'
                if primeros_4_num_account != '0134':
                    if self.use_alternal_nomina_txt:
                        raise UserError("No se puede ejecutar un txt nomina con cuentas de distintos bancos") 
                    last_num = '425'
                email = ''
                if wh.employee_id.personal_email or wh.employee_id.work_email :
                    email =''# wh.employee_id.personal_email or wh.employee_id.work_email
                partner_name = (nombre).replace(",","").replace(".","").replace("'","")
                replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                partner= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], partner_name)
                content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                    num2.ljust(2),
                    num_restante.ljust(8).zfill(8),
                    space.ljust(22),
                    amount_cal.ljust(15),
                    ves1.ljust(3),
                    cuenta.ljust(20),
                    space.ljust(10),
                    primeros_4_num_account.ljust(4),
                    space.ljust(10),
                    primera_letra_rif_partner.ljust(1),
                    restante_rif.ljust(9),
                    space.ljust(7),
                    partner[:45].ljust(45),
                    space.ljust(25),
                    email.ljust(40),
                    space.ljust(161),
                    last_num,
                )

        # 
        standard = '06'
        can = str(1).zfill(15) 
        can2 = str(len(self.slip_ids.filtered(lambda x:x.state!='cancel'))).zfill(15)
        monto_total = sum(self.slip_ids.filtered(lambda x:x.state!='cancel').mapped('total_sum'))
        amount_cal = "{0:.2f}".format(monto_total)
        total_amount = rs.join(amount_cal.split('.')).zfill(15)  
        content += '%s%s%s%s\n'%(
            standard.ljust(2),
            can.ljust(15),
            can2.ljust(15),
            total_amount[:15].ljust(15)
        )    
        return self.get_txt(content, "banesco")
        
        
    def txt_provincial(self,bank=None):
        lines = []
        if self.use_alternal_nomina_txt:
            raise UserError("Aun no se a añadido esta txt nómina para este banco")
        for slip in self.slip_ids.filtered(lambda x:x.state!='cancel') :
            if slip.employee_id.has_autorized:
                    cedula = slip.employee_id.ci_autorizate[0]
                    cedula_v = slip.employee_id.ci_autorizate[1:]
                    cuenta=slip.employee_id.account_number_autorizate
                    nombre=slip.employee_id.name_autorizate
            else:
                    cedula = slip.employee_id.nationality
                    cuenta=slip.employee_id.account_number_2
                    cedula_v = slip.employee_id.identification_id_2
                    nombre=slip.employee_id.name
            lines.append(
                "".join([
                    str(cuenta or 3854)+" "+str(slip.id or "384").zfill(8)+" "+(cedula or "V")[:1].upper()+str(cedula_v or "384").zfill(9)+" "+ 
                    (self.format_monto(slip.monto) or " ").zfill(17)+" "+(slip.employee_id.lastname or " "),
                    nombre
                ])
            )
        
        return self.get_txt(lines, "provincial")
    
    def txt_caribe(self,bank=None):
        lines = []

        for slip in (self.filter_by_bank(self.slips_filtered,bank) if bank else self.slips_filtered()) :
            if slip.employee_id.has_autorized:
                    cedula = slip.employee_id.ci_autorizate[0]
                    cedula_v = slip.employee_id.ci_autorizate[1:]
                    cuenta=slip.employee_id.account_number_autorizate
                    nombre=slip.employee_id.name_autorizate
            else:
                    cedula = slip.employee_id.nationality
                    cuenta=slip.employee_id.account_number_2
                    cedula_v = slip.employee_id.identification_id_2
                    nombre=slip.employee_id.name
            lines.append(
                "/".join([
                    "3" if slip.employee_id.account_type_2 == "0" else "4",
                    str(cuenta),
                    str(round(self.convert(slip.monto), 2)),
                    nombre.upper(),
                    str(slip.id)
                ])
            )


        return self.get_txt(lines, "caribe")
    
    def txt_venezuela(self,bank=None):
        rs=','
        content = ''
        date = datetime.now().strftime("%d/%m/%Y").replace("/", "")
        nombre_archivo = 'PROVE_'+ str(date) +'.txt'
        if self.use_alternal_nomina_txt:
            raise UserError("Aun no se a añadido esta txt nómina para este banco")

        head = 'HEADER'
        namen=self.name
        string_lote = namen.replace("/", "")
        num_lote = ''.join([i for i in string_lote if not i.isalpha()])
        num_nego = '00654564'
        first_letter_rif = self.company_id.vat[0]
        rest_rif = self.company_id.vat[2:]
        if first_letter_rif == 'J':
            rest_rif = rest_rif[:9]
        fecha = datetime.now().strftime("%d/%m/%Y")
        content += '%s%s%s%s%s%s%s\n'%(
            head.ljust(8),
            num_lote.ljust(8),
            num_nego.ljust(8),
            first_letter_rif.ljust(1),
            rest_rif.ljust(9),
            fecha.ljust(10),
            fecha.ljust(10)
        )
        for wh in self.slip_ids.filtered(lambda x:x.state!='cancel'):
                    if wh.employee_id.has_autorized:
                        cedula_v = wh.employee_id.ci_autorizate
                        cuenta=wh.employee_id.account_number_autorizate
                        nombre=wh.employee_id.name_autorizate
                        banco=wh.employee_id.bank_autorizate
                    else:
                        cedula = wh.employee_id.identification_id_2
                        cuenta=wh.employee_id.account_number_2
                        cedula_v = wh.employee_id.rif.replace("-", "")
                        nombre=wh.employee_id.name
                        banco=wh.employee_id.bank_account_id_emp_2

                    if not  cuenta:
                        raise UserError('No le ha registrado Cuentas Bancarias al empleado')
                    ################### linea de debito##################
                    debito = 'DEBITO'
                    namin=wh.name
                    num_ref= namin.replace("/","")
                    num_ref = ''.join([i for i in num_ref if not i.isalpha()])
                    referencia = num_ref[-8:]
                    first_letter_rif = self.company_id.vat[0]
                    rest_rif = self.company_id.vat[2:]
                    if first_letter_rif == 'J':
                        rest_rif = rest_rif[:9]
                    name_comp = (self.company_id.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    company= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], name_comp)
                    date = self.date_start.strftime("%d/%m/%Y")
                    code = 'VEB40'
                    cero='00'
                    monto= (wh.total_sum)
                    amount_cal = "{0:.2f}".format(monto)
                    amount = rs.join(str(amount_cal).split('.')).zfill(18)
                    content += '%s%s%s%s%s%s%s%s%s%s\n'%(
                        debito.ljust(8),
                        referencia[:8].ljust(8),
                        first_letter_rif.ljust(1),
                        rest_rif[:9].ljust(9),
                        company[:35].ljust(35),
                        date.ljust(10),
                        cero.ljust(2),
                        self.journal_id.bank_account_id.acc_number.ljust(20),
                        amount[:18].ljust(18),
                        code.ljust(5)
                    )
                    ################### linea de credito##################
                    primera_letra_rif = cedula_v[0] if cedula_v else ''
                    restante_rif = cedula_v[2:] if cedula_v else ''
                    if primera_letra_rif =='V':
                        restante_rif= restante_rif[:8]
                    restante_rif  = restante_rif.zfill(9)
                    credit = 'CREDITO'
                    digit_cuenta = ''
                    digit_swift = ''
                    # if header.payment_ids.filtered( lambda y: y.tipo_de_cuenta == 'corriente'):
                    if wh.employee_id.account_type_2 == 0:
                        digit_cuenta = '00'
                        digit_swift = '10'
                    else:
                        digit_cuenta = '01'
                        digit_swift = '00'
                    email = ''
                    if wh.employee_id.personal_email or wh.employee_id.work_email :
                        email = wh.employee_id.personal_email or wh.employee_id.work_email
                    monto= (wh.total_sum)
                    amount_cal = "{0:.2f}".format(monto)
                    amount = rs.join(str(amount_cal).split('.')).zfill(18)
                    if not banco.bic:
                        raise UserError('Debe tener asignado el código Swift del banco')
                    partner_name = (nombre).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], partner_name)
                    content += '%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        credit.ljust(8),
                        referencia[:8].ljust(8),
                        primera_letra_rif.ljust(1),
                        restante_rif[:9].ljust(9),
                        partner.ljust(30),
                        digit_cuenta.ljust(2),
                        cuenta.ljust(20),
                        amount[:18].ljust(18),
                        digit_swift.ljust(2),
                        banco.bic.ljust(19),
                        email.ljust(50),
                    )
                    
                
        total = 'TOTAL'
        can1 = str(len(self.slip_ids.filtered(lambda x:x.state!='cancel'))).zfill(5)
        monto_total = sum(self.slip_ids.filtered(lambda x:x.state!='cancel').mapped('total_sum'))
        amount_cal = "{0:.2f}".format(monto_total)
        amount = rs.join(str(amount_cal).split('.')).zfill(18)
        content += '%s%s%s%s\n'%(
            total.ljust(8),
            can1.ljust(5),
            can1.ljust(5),
            amount[:18].ljust(18)
        )
        return self.get_txt(content, "venezuela")

     
    def read_response_provincial(self, text):
        lines = [re.split("\s+", line)[1][23:-20].lstrip("0") for line in text if "AUTORIZADO" in line]   

        self.pagada_slip(lines)

    def read_response_mercantil(self, text):
        # id = re.split("\s{2,}", text.pop(0))[1][-4:]

        # if id != self.mercantil_number:
        #     raise UserError("El archivo de respuesta tiene un ID diferente al esperado")
        lines = [l[-31:-23].lstrip("0") for l in text if "COBRO EXITOSO" in l]
        
        self.pagada_slip(lines)

    def read_response_banesco(self, text):        
        lines = [text[i][2:] for i in range(0, len(text), 2) if "COBRO EXITOSO" in text[i + 1]]

        self.pagada_slip(lines)

    def read_response_bod(self, text):
        lines = [l.strip()[-26:-19].lstrip("0") for l in text if "REGISTRO PROCESADO" in l]

        self.pagada_slip(lines)

    def read_response_venezolano_credito(self, text):
        lines = [[w.strip() for w in re.split("\s{2,}", l.strip())][-4].lstrip("0") for l in text if "CARCARGADO" in l]
        
        self.pagada_slip(lines)

    def read_response_caribe(self, accounts):
            slips = self.slip_ids.sorted("date_from").filtered(lambda c: c.state != "done")

            for i, account in [(accounts.count(account), account) for account in set(accounts)]:
                slips \
                    .filtered(lambda c: c.employee_id.account_number_2 == account)[0:i] \
                    .write({"state":"done"})
    #endregion

    #region Lectura de archivos
    def button_sent_txt(self):
        for rec in self:
            if not rec.slip_ids:
                raise ValidationError("Las nóminas no deben estar vacías")

            if not rec.bank_code:
                raise ValidationError("El banco no está asignado")

            if not rec.company_rif:
                raise ValidationError("La compañía debe tener RIF")
            if len(set(self.mapped("bank_code")))>1:
                raise UserError("Los lotes elegidos no poseen un mismo banco, porfavor seleccione lotes con un banco en comun")
            
            runs_ids='_'.join(map(str,self.ids))

            return {
            'type'  : 'ir.actions.act_url',
            'url'   : f"/ediTXTNomina/{runs_ids}",
            'target': 'new',
            'res_id': self.ids,
            'context':{'target':'flush'}
        }
    def handle_xls_response(self):
        file = xlrd.open_workbook(file_contents=base64.decodestring(self.file)).sheets()[0]

        exitosa = lambda l: l[-2] == "TRANSACCION EXITOSA"

        text = list(filter(exitosa, [[file.cell(row, col).value.strip() for col in range(file.ncols)] for row in range(file.nrows)][1:]))

        self.read_response_caribe([t[0] for t in text])

    def handle_txt_response(self):
        text = base64.b64decode(self.file).decode()

        patterns = {
            "provincial": ".REC", 
            "mercantil": "1BAMRVECA", 
            "banesco": "UNIOVECA", 
            "venezolano_credito": "CO0001500000",
            "bod": "BOD",
        }

        banks_codes = dict(zip(patterns.keys(), ("0108", "0105", "0134", "0104", "0116")))

        for bank, pattern in patterns.items():
            if pattern in text:
                if banks_codes[bank] != self.bank_code:
                    raise UserError("La respuesta no es del mismo banco registrado")

                getattr(self, f"read_response_{bank}")([t.strip() for t in text.rsplit("\n")])

                break
        else:
            if not any([pattern in text for pattern in patterns]):
                raise UserError("El archivo subido no es una respuesta válida")

    
    #endregion
    @api.onchange('vacation','check_special_struct')
    def domain_struct(self):
        for rec in self:
            domain=[]
            
            if rec.vacation:
                domain.append(('struct_category', '=', 'vacation'))
            elif rec.check_special_struct:
                domain.append(('struct_category', '=', 'especial'))
            else:
                domain.append(('struct_category', '=', 'normal'))

            return {'domain': {'struct_id': domain}}


    def receive_answer_bank(self):
        pass


    def go_to_account_moves(self):
        ids=[]
        name=''
        for rec in self:
            next_ids=rec.slip_ids.filtered(lambda x: x.state=="done").mapped('move_id.id')
            ids=ids+next_ids

        return {
            "type"      : "ir.actions.act_window",
            "name"      : "Asientos lote seleccionados",
            "res_model" : 'account.move',
            "view_mode" : "tree,form",
            "domain"    : [("id", "in", ids)],
            "target"    : "current",
        }

    def write(self,vals):
        res = super().write(vals)
        if vals.get("incidence_line_ids"):
            self.message_post(body=f"Se aplicaron cambios en las incidencias: {self.incidence_line_ids}")
        return res

    @api.constrains('incidence_line_ids','date_end','date_start')
    def contrain_incidences(self):
        for rec in self:
            for line in rec.incidence_line_ids:
                if line.fecha_ini<rec.date_start or line.fecha_fin>rec.date_end:
                    raise UserError("El rango de fecha que intenta colocar, va a producir inconsistencia con las incidencias")
                if line.category_id!=rec.category_id_filter:
                    raise UserError("Hay discrepancia entre la categoria de la incidencia y del lote")
            if rec.incidence_line_ids.filtered(lambda x:x.hours_or_days=="day" and  x.number_of_unit>((rec.date_end-rec.date_start).days+1)) or rec.incidence_line_ids.filtered(lambda x:x.hours_or_days=="hour" and  x.number_of_unit>((rec.date_end-rec.date_start).days*24+24)):
                raise UserError("NO se pueden colocar Incidencias cuyo valor superen el rango del lote")
            
#endregion