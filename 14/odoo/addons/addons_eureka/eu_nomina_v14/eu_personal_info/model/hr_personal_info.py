# -*- coding: utf-8 -*-
########################################################################################################################
#    Change: jeduardo **  05/07/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para la ficha del trabajador
# -----------------------------------------------------------------------------
#    Modified by: k-pérez 2020/10/02
#    Type of change: migration v11 to v13
#    Comments: Field validations, removed unused statements, refactor, class changed to CamelCase.
# ######################################################################################################################

from odoo import fields, models, _, exceptions, api
# importando el modulo de regex de python
import re
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta

_DATETIME_FORMAT = "%Y-%m-%d"


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = "hr.employee"
    _description = "Personal info employee"
    passport_id = fields.Char('Passport No', groups="hr.group_hr_user", size=20)

    GRUPO_SANGUINEO = [
        ('O', 'O'),
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB')]

    FACTOR_RH = [
        ('positivo', 'Positivo'),
        ('negativo', 'Negativo')]

    MARITAL_STATUS = [
        ('S', 'Soltero'),
        ('C', 'Casado'),
        ('U', 'Unión estable de hecho'),
        ('V', 'Vuido'),
        ('D', 'Divorciado'),
    ]

    NVEL_EDUCATIVO = [
        ('01', u'Básica'),
        ('02', 'Bachiller'),
        ('03', 'TSU'),
        ('04', 'Universitario'), ]

    NACIONALIDAD = [
        ('V', 'Venezolano'),
        ('E', 'Extranjero')]

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        # ('other', 'Other')
    ],tracking=True)

    identification_id_2 = fields.Char('Cédula de identidad', size=15,tracking=True)
    nationality = fields.Selection(NACIONALIDAD, string='Tipo documento', required=False,tracking=True)
    rif = fields.Char('Rif', size=15, required=False,tracking=True)
    personal_email = fields.Char('Correo electrónico personal', size=240, required=False,tracking=True)
    education = fields.Selection(NVEL_EDUCATIVO, 'Nivel educativo',tracking=True)
    profesion_id = fields.Many2one('hr.profesion', 'Profesión',tracking=True)
    country_birth_id = fields.Many2one('res.country', 'País de nacimiento',tracking=True)  # PAIS DE NACIMIENTO
    state_id = fields.Many2one('res.country.state', 'Estado', domain="[('country_id','=',238)]",tracking=True) # ESTADO DE NACIMIENTO
    city_id = fields.Many2one('res.country.state.city', 'Ciudad',tracking=True)  
    employee_age = fields.Integer("Edad", compute='_calcular_edad',tracking=True)
    marriage_certificate = fields.Boolean('¿Entregó acta de matrimonio?',tracking=True)
    marital_2 = fields.Selection(MARITAL_STATUS, 'Estado civil',tracking=True)
    # Nro_de_Hijos = fields.Integer('Numero de hijos', size=2)
    grupo_sanguineo = fields.Selection(GRUPO_SANGUINEO, 'Grupo Sanguíneo',tracking=True)
    factor_rh = fields.Selection(FACTOR_RH, 'Factor RH',tracking=True)
    # INFORMACION DE CONTACTO
    street = fields.Char('Av./Calle', size=50,tracking=True)
    house = fields.Char('Edif. Quinta o Casa', size=50,tracking=True)
    piso = fields.Char('Piso', size=2,tracking=True)
    apto = fields.Char('N° de apartamento.', size=50,tracking=True)
    state_id_res = fields.Many2one('res.country.state', 'Estado de nacimiento', domain="[('country_id','=',238)]")
    city_id_res = fields.Many2one('res.country.state.city', 'Ciudad  de nacimiento')# CIUDAD DE NACIMIENTO
    telf_hab = fields.Char('Telefono de Habitación', size=12)
    telf_contacto = fields.Char('Telefono Contacto', size=12)
    e_municipio = fields.Many2one('res.country.state.municipality', 'Municipio', size=100)
    e_parroquia = fields.Many2one('res.country.state.municipality.parish', 'Parroquia', size=100)
    code_postal = fields.Char('Código Postal', size=4,tracking=True)
    #  birthday = fields.Many2one('hr.employee','Fecha de Nacimiento')
    coach_id = fields.Many2one('hr.employee', 'Coach')
    # var_state = fields.Char()
    var_aux = fields.Char()

    @api.onchange('address_home_id')
    def _onchange_address_home_id(self):
        for rec in self:
            if rec.address_home_id:
                rec.rif=rec.address_home_id.vat
                rec.personal_email=rec.address_home_id.email
                rec.country_id=rec.address_home_id.country_id
                rec.state_id=rec.address_home_id.state_id
                rec.city_id=rec.address_home_id.city_id
                rec.e_municipio=rec.address_home_id.municipality_id
                rec.e_parroquia=rec.address_home_id.parish_id
                rec.street=rec.address_home_id.street
                rec.code_postal=rec.address_home_id.zip
                rec.telf_hab=rec.address_home_id.phone
                rec.telf_contacto=rec.address_home_id.mobile
                rec.identification_id_2=rec.address_home_id.cedula
                rec.name=rec.address_home_id.name
    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            self.var_aux = self.state_id


    # @api.onchange('state_id_res')
    # def _onchange_state(self):
    #     self.city_id_res = False
    #     self.e_municipio = False
    #     self.e_parroquia = False
    #     if self.state_id_res:
    #         self.var_state = self.state_id_res.state_id_res

    @api.onchange('city_id_res')
    def _onchange_city(self):
        self.e_municipio = False
        self.e_parroquia = False

    @api.onchange('e_municipio')
    def _onchange_municipio(self):
        self.e_parroquia = False
        
   

    def validate_email_addrs(self, email):
        res = {}

        mail_obj = re.compile(r"""
                \b             # comienzo de delimitador de palabra
                [\w.%+-]       # usuario: Cualquier caracter alfanumerico mas los signos (.%+-)
                +@             # seguido de @
                [\w.-]         # dominio: Cualquier caracter alfanumerico mas los signos (.-)
                +\.            # seguido de .
                [a-zA-Z]{2,8}  # dominio de alto nivel: 2 a 6 letras en minúsculas o mayúsculas.
                \b             # fin de delimitador de palabra
                """, re.X)  # bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar
        # el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
        if mail_obj.search(email):
            return True
        else:
            return False
    def validate_cedula(self, cedula):
        res = {}

        cedula_obj = re.compile(r"""^[JVE]{1}\d{5,}$""", re.X)  # bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar
        # el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
        if cedula_obj.search(cedula):
            return True
        else:
            return False


    def validacion_cedula(self, valor):
        if not self.validate_cedula(valor):
            raise UserError('¡Advertencia! La cédula debe tener el Formato V21874658')
        # if (len(valor) > 8) or (len(valor) < 7):
        #     raise exceptions.except_orm('¡Advertencia!',
        #                                 u'El número de cédula no puede ser menor que 7 cifras ni mayor a 8.')
        busqueda = self.env['hr.employee'].search([('identification_id_2', '!=', 0)])
        for a in busqueda:
            if a.identification_id_2 == valor:
                raise UserError('¡Advertencia! El número de Cédula ya se encuentra registrado')
        return

    @staticmethod
    def _fecha_nacimiento_permitida(fecha_inicio, fecha_fin):
        if datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT) >= datetime.strptime(fecha_inicio,
                                                                                         DEFAULT_SERVER_DATE_FORMAT):
            return True
        else:
            return False

    @api.onchange('birthday')
    @api.depends('birthday')
    def _calcular_edad(self):
        for record in self:
            # Eliminé iteración sobre el booleano: record.birthday[0]
            if record.birthday:
                fecha_fin = date.today()
                fecha_inicio = record.birthday
                # Añadí str(fechas)
                fecha_permitida = self._fecha_nacimiento_permitida(str(fecha_inicio), str(fecha_fin))
                if fecha_permitida:
                    antiguedad = relativedelta.relativedelta(datetime.strptime(str(fecha_fin),
                                                                               DEFAULT_SERVER_DATE_FORMAT),
                                                             datetime.strptime(str(fecha_inicio),
                                                                               # Añadí str(fechas)
                                                                               DEFAULT_SERVER_DATE_FORMAT))
                    years = antiguedad.years
                    record.employee_age = years
                else:
                    raise UserError('¡Advertencia! La fecha de nacimiento introducida "%s" no puede ser mayor a la actual!' % fecha_inicio)
            else:
                record.employee_age = 0

    def onchange_rif_er(self, field_value):
        res = {}

        if field_value:
            res = self.validate_rif_er(field_value)
            if not res:
                raise UserError('¡Advertencia!El rif tiene el formato incorrecto. Ej: V-012345678 o E-012345678. Por favor intente de nuevo')
        return {'value': res}

    def validate_rif_er(self, field_value):
        res = {}

        rif_obj = re.compile(r"^[V|E]-[\d]{9}", re.X)
        if rif_obj.search(field_value):
            res = {
                'rif': field_value
            }
        return res

    def write(self, vals):
        # res = {}

        if vals.get('identification_id_2'):
            valor = vals.get('identification_id_2')
            self.validacion_cedula(valor)
        if vals.get('rif'):
            res = self.validate_rif_er(vals.get('rif'))
            if not res:
                raise exceptions.except_orm('¡Advertencia!',
                                            'El rif tiene el formato incorrecto. '
                                            'Ej: V-012345678 o E-012345678. Por favor intente de nuevo')
        # if vals.get('personal_email'):
        #     res = self.validate_email_addrs(vals.get('personal_email'), 'personal_email')
        #     if not res:
        #         raise exceptions.except_orm('Advertencia!',
        #                                     'El email es incorrecto. Ej: cuenta@dominio.xxx. '
        #                                     'Por favor intente de nuevo')
        if vals.get('telf_hab'):
            res = self.validate_phone_number(vals.get('telf_hab'), 'telf_hab')
            if not res:
                raise exceptions.except_orm('¡Advertencia!',
                                            u'El número telefónico tiene el formato incorrecto. '
                                            u'Ej: 0123-4567890. Por favor intente de nuevo')
        if vals.get('telf_contacto'):
            res = self.validate_phone_number(vals.get('telf_contacto'), 'telf_contacto')
            if not res:
                raise exceptions.except_orm('¡Advertencia!',
                                            u'El número telefónico tiene el formato incorrecto. '
                                            u'Ej: 0123-4567890. Por favor intente de nuevo')
        if vals.get('code_postal'):
            res = self.validate_code_postal(vals.get('code_postal'))
            if not res:
                raise exceptions.except_orm('¡Advertencia!',
                                            u'El código postal debe contener solo números. Ej. 1000')

        return super(HrEmployee, self).write(vals)

    @api.model
    def create(self, vals):

        if self._context is None:
            context = {}
            res = {}

        if vals.get('identification_id_2'):
            valor = vals.get('identification_id_2')
            self.validacion_cedula(valor)

        if vals.get('rif'):
            res = self.validate_rif_er(vals.get('rif'))
            if not res:
                raise exceptions.except_orm('¡Advertencia!',
                                            'El rif tiene el formato incorrecto. Ej: V-012345678 o E-012345678. '
                                            'Por favor intente de nuevo')
        # if vals.get('personal_email'):
        #     res = self.validate_email_addrs(vals.get('personal_email'), 'personal_email')
        #     if not res:
        #         raise exceptions.except_orm('¡Advertencia!',
        #                                     'El email es incorrecto. Ej: cuenta@dominio.xxx. '
        #                                     'Por favor intente de nuevo')
        if vals.get('telf_hab'):
            res = self.validate_phone_number(vals.get('telf_hab'), 'telf_hab')
            if not res:
                raise exceptions.except_orm('¡Advertencia!',
                                            u'El número telefónico tiene el formato incorrecto. '
                                            u'Ej: 0123-4567890. Por favor intente de nuevo')
        if vals.get('telf_contacto'):
            res = self.validate_phone_number(vals.get('telf_contacto'), 'telf_contacto')
            if not res:
                raise exceptions.except_orm('¡Advertencia!',
                                            u'El número telefónico tiene el formato incorrecto. '
                                            u'Ej: 0123-4567890. Por favor intente de nuevo')

        if vals.get('code_postal'):
            res = self.validate_code_postal(vals.get('code_postal'))
            if not res:
                raise exceptions.except_orm('¡Advertencia!',
                                            u'El código postal debe contener solo números. Ej. 1000')
        res = super(HrEmployee, self).create(vals)
        return res

    def validate_code_postal(self, valor):
        res = {}
        code_obj = re.compile(r"""^\d{4}""", re.X)
        if code_obj.search(valor):
            res = {
                'code_postal': valor
            }
        return res


HrEmployee()


class HrProfesion(models.Model):

    def _get_profesion_position(self):
        res = []
        for employee in self.env('hr.employee').browse(self):
            if employee.profesion_id:
                res.append(employee.profesion_id.id)
        return res

    _name = "hr.profesion"
    _description = "Profesion Description"

    name = fields.Char('Profesion Name', size=128, required=True, index=True)
    # 'employee_ids': fields.one2many('hr.employee', 'profesion_id', 'Employees'),





class EmployeePublic(models.Model):
    _inherit = "hr.employee.public"
    _description = "Passport employee"
    passport_id = fields.Char('Passport No', groups="hr.group_hr_user", size=20)

    GRUPO_SANGUINEO = [
        ('O', 'O'),
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB')]

    FACTOR_RH = [
        ('positivo', 'Positivo'),
        ('negativo', 'Negativo')]

    MARITAL_STATUS = [
        ('S', 'Soltero'),
        ('C', 'Casado'),
        ('U', 'Unión estable de hecho'),
        ('V', 'Vuido'),
        ('D', 'Divorciado'),
    ]

    NVEL_EDUCATIVO = [
        ('01', u'Básica'),
        ('02', 'Bachiller'),
        ('03', 'TSU'),
        ('04', 'Universitario'), ]

    NACIONALIDAD = [
        ('V', 'Venezolano'),
        ('E', 'Extranjero')]

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        # ('other', 'Other')
    ])

    identification_id_2 = fields.Char('Cédula de identidad', size=8)
    nationality = fields.Selection(NACIONALIDAD, string='Tipo documento', required=False)
    rif = fields.Char('Rif', size=11, required=False)
    personal_email = fields.Char('Correo electrónico personal', size=240, required=False)
    education = fields.Selection(NVEL_EDUCATIVO, 'Nivel educativo')
    profesion_id = fields.Many2one('hr.profesion', 'Profesión')
    country_birth_id = fields.Many2one('res.country', 'País de nacimiento')  # PAIS DE NACIMIENTO
    state_id = fields.Many2one('res.country.state', 'Estado', domain="[('country_id','=',238)]") # ESTADO DE NACIMIENTO
    city_id = fields.Many2one('res.country.state.city', 'Ciudad')  
    marriage_certificate = fields.Boolean('¿Entregó acta de matrimonio?')
    marital_2 = fields.Selection(MARITAL_STATUS, 'Estado civil')
    # Nro_de_Hijos = fields.Integer('Numero de hijos', size=2)
    grupo_sanguineo = fields.Selection(GRUPO_SANGUINEO, 'Grupo Sanguíneo')
    factor_rh = fields.Selection(FACTOR_RH, 'Factor RH')
    # INFORMACION DE CONTACTO
    street = fields.Char('Av./Calle', size=50)
    house = fields.Char('Edif. Quinta o Casa', size=50)
    piso = fields.Char('Piso', size=2)
    apto = fields.Char('N° de apartamento.', size=50)
    state_id_res = fields.Many2one('res.country.state', 'Estado de nacimiento', domain="[('country_id','=',238)]")
    city_id_res = fields.Many2one('res.country.city', 'Ciudad  de nacimiento')# CIUDAD DE NACIMIENTO
    telf_hab = fields.Char('Telefono de Habitación', size=12)
    telf_contacto = fields.Char('Telefono Contacto', size=12)
    e_municipio = fields.Many2one('res.country.state.municipality', 'Municipio', size=100)
    e_parroquia = fields.Many2one('res.country.state.municipality.parish', 'Parroquia', size=100)
    code_postal = fields.Char('Código Postal', size=4)
    #  birthday = fields.Many2one('hr.employee','Fecha de Nacimiento')
    coach_id = fields.Many2one('hr.employee', 'Coach')
    # var_state = fields.Char()
    var_aux = fields.Char()

    # @api.onchange('state_id')
    # def _onchange_state_id(self):
    #     if self.state_id:
    #         self.var_aux = self.state_id.res_state_ve_id


    # @api.onchange('state_id_res')
    # def _onchange_state(self):
    #     self.city_id_res = False
    #     self.e_municipio = False
    #     self.e_parroquia = False
    #     if self.state_id_res:
    #         self.var_state = self.state_id_res.res_state_ve_id

    # @api.onchange('city_id_res')
    # def _onchange_city(self):
    #     self.e_municipio = False
    #     self.e_parroquia = False

    # @api.onchange('e_municipio')
    # def _onchange_municipio(self):
    #     self.e_parroquia = False
        

    # def onchange_email_addr(self, email, field):
    #     res = {}

    #     if email:
    #         res = self.validate_email_addrs(email, field)
    #         if not res:
    #             raise exceptions.except_orm(_('¡Advertencia!'), _(
    #                 'El email es incorrecto. Ej: cuenta@dominio.xxx. Por favor intente de nuevo'))
    #     return {'value': res}

    # def validate_email_addrs(self, email, field):
    #     res = {}

    #     mail_obj = re.compile(r"""
    #             \b             # comienzo de delimitador de palabra
    #             [\w.%+-]       # usuario: Cualquier caracter alfanumerico mas los signos (.%+-)
    #             +@             # seguido de @
    #             [\w.-]         # dominio: Cualquier caracter alfanumerico mas los signos (.-)
    #             +\.            # seguido de .
    #             [a-zA-Z]{2,3}  # dominio de alto nivel: 2 a 6 letras en minúsculas o mayúsculas.
    #             \b             # fin de delimitador de palabra
    #             """, re.X)  # bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar
    #     # el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
    #     if mail_obj.search(email):
    #         res = {
    #             field: email
    #         }
    #     return res

    # def onchange_phone_number(self, phone, field):
    #     res = {}
    #     if phone:
    #         res = self.validate_phone_number(phone, field)
    #         if not res:
    #             raise exceptions.except_orm(_('¡Advertencia!'), _(
    #                 u'El número telefónico tiene el formato incorrecto. Ej: 0123-4567890. Por favor intente de nuevo'))
    #     return {'value': res}

    # def validate_phone_number(self, phone, field):
    #     self.field = field
    #     res = {}

    #     phone_obj = re.compile(r"""^0\d{3}-\d{7}""", re.X)
    #     # ^: inicio de linea
    #     # 0\d{3}: codigo de area: cuantro (4) caracteres numericos comenzando con 0
    #     # -: seguido de -
    #     # \d{7}: numero de telefono: cualquier caracter numerico del 0 al 9. 7 numeros
    #     # re.X: bandera de compilacion X: habilita la modo verborrágico,
    #     # el cual permite organizar el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
    #     if phone_obj.search(phone):
    #         res = {
    #             field: phone
    #         }
    #     return res

    # def validacion_cedula(self, valor):
    #     if not valor.isdigit():
    #         raise exceptions.except_orm('¡Advertencia!', u'La cédula solo debe contener números')
    #     if (len(valor) > 8) or (len(valor) < 7):
    #         raise exceptions.except_orm('¡Advertencia!',
    #                                     u'El número de cédula no puede ser menor que 7 cifras ni mayor a 8.')
    #     busqueda = self.env['hr.employee'].search([('identification_id_2', '!=', 0)])
    #     for a in busqueda:
    #         if a.identification_id_2 == valor:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         u'El número de Cédula ya se encuentra registrado')
    #     return

    # @staticmethod
    # def _fecha_nacimiento_permitida(fecha_inicio, fecha_fin):
    #     if datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT) >= datetime.strptime(fecha_inicio,
    #                                                                                      DEFAULT_SERVER_DATE_FORMAT):
    #         return True
    #     else:
    #         return False

    

    # def onchange_rif_er(self, field_value):
    #     res = {}

    #     if field_value:
    #         res = self.validate_rif_er(field_value)
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         'El rif tiene el formato incorrecto. Ej: V-012345678 o E-012345678.'
    #                                         'Por favor intente de nuevo')
    #     return {'value': res}

    # def validate_rif_er(self, field_value):
    #     res = {}

    #     rif_obj = re.compile(r"^[V|E]-[\d]{9}", re.X)
    #     if rif_obj.search(field_value):
    #         res = {
    #             'rif': field_value
    #         }
    #     return res

    # def write(self, vals):
    #     # res = {}

    #     if vals.get('identification_id_2'):
    #         valor = vals.get('identification_id_2')
    #         self.validacion_cedula(valor)
    #     if vals.get('rif'):
    #         res = self.validate_rif_er(vals.get('rif'))
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         'El rif tiene el formato incorrecto. '
    #                                         'Ej: V-012345678 o E-012345678. Por favor intente de nuevo')
    #     if vals.get('personal_email'):
    #         res = self.validate_email_addrs(vals.get('personal_email'), 'personal_email')
    #         if not res:
    #             raise exceptions.except_orm('Advertencia!',
    #                                         'El email es incorrecto. Ej: cuenta@dominio.xxx. '
    #                                         'Por favor intente de nuevo')
    #     if vals.get('telf_hab'):
    #         res = self.validate_phone_number(vals.get('telf_hab'), 'telf_hab')
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         u'El número telefónico tiene el formato incorrecto. '
    #                                         u'Ej: 0123-4567890. Por favor intente de nuevo')
    #     if vals.get('telf_contacto'):
    #         res = self.validate_phone_number(vals.get('telf_contacto'), 'telf_contacto')
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         u'El número telefónico tiene el formato incorrecto. '
    #                                         u'Ej: 0123-4567890. Por favor intente de nuevo')
    #     if vals.get('code_postal'):
    #         res = self.validate_code_postal(vals.get('code_postal'))
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         u'El código postal debe contener solo números. Ej. 1000')

    #     return super(HrEmployee, self).write(vals)

    # @api.model
    # def create(self, vals):

    #     if self._context is None:
    #         context = {}
    #         res = {}

    #     if vals.get('identification_id_2'):
    #         valor = vals.get('identification_id_2')
    #         self.validacion_cedula(valor)

    #     if vals.get('rif'):
    #         res = self.validate_rif_er(vals.get('rif'))
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         'El rif tiene el formato incorrecto. Ej: V-012345678 o E-012345678. '
    #                                         'Por favor intente de nuevo')
    #     if vals.get('personal_email'):
    #         res = self.validate_email_addrs(vals.get('personal_email'), 'personal_email')
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         'El email es incorrecto. Ej: cuenta@dominio.xxx. '
    #                                         'Por favor intente de nuevo')
    #     if vals.get('telf_hab'):
    #         res = self.validate_phone_number(vals.get('telf_hab'), 'telf_hab')
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         u'El número telefónico tiene el formato incorrecto. '
    #                                         u'Ej: 0123-4567890. Por favor intente de nuevo')
    #     if vals.get('telf_contacto'):
    #         res = self.validate_phone_number(vals.get('telf_contacto'), 'telf_contacto')
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         u'El número telefónico tiene el formato incorrecto. '
    #                                         u'Ej: 0123-4567890. Por favor intente de nuevo')

    #     if vals.get('code_postal'):
    #         res = self.validate_code_postal(vals.get('code_postal'))
    #         if not res:
    #             raise exceptions.except_orm('¡Advertencia!',
    #                                         u'El código postal debe contener solo números. Ej. 1000')
    #     res = super(HrEmployee, self).create(vals)
    #     return res

    # def validate_code_postal(self, valor):
    #     res = {}
    #     code_obj = re.compile(r"""^\d{4}""", re.X)
    #     if code_obj.search(valor):
    #         res = {
    #             'code_postal': valor
    #         }
    #     return res

'''
class hr_ciudad(models.Model):

    def _get_ciudad_position(self):
        res = []
        for employee in self.env('hr.employee').browse(self):
            if employee.city_id:
                res.append(employee.city_id.id)
        return res

    _name = "hr.ciudad"
    _description = "Ciudad Description"

    name= fields.Char('Ciudad Name', size=50, required=True, select=True)
    #employee_ids= fields.One2many('hr.employee', 'city_id', 'Employees')
    estate_id = fields.Many2one('res.country.city', 'Estado')


hr_ciudad()


class hr_municipio(models.Model):

    def _get_municipio_position(self):
        res = []
        for employee in self.env['hr.employee'].browse():
            if employee.municipio_id:
                res.append(employee.municipio_id.id)
        return res

    _name = "hr.municipio"
    _description = "Municipio Description"

    name = fields.Char('Municipio', size=128, required=True, select=True)
   # employee_ids = fields.One2many('hr.employee', 'municipio_id', 'Employees')
    ciudad_id = fields.Many2one('res.country.city', 'Ciudad')
    estate_id = fields.Many2one('res.country.state', 'Estado')


hr_municipio()

class hr_parroquia(models.Model):

    def _get_parroquia_position(self):
        res = []
        for employee in self.env['hr.employee'].browse():
            if employee.parroquia_id:
                res.append(employee.parroquia_id.id)
        return res

    _name = "hr.parroquia"
    _description = "Parroquia Description"

    name = fields.Char('Parroquia', size=128, required=True, select=True)
   # employee_ids = fields.One2many('hr.employee', 'parroquia_id', 'Employees')
    municipio_id = fields.Many2one('hr.municipio', 'Municipio')


hr_parroquia()
'''
