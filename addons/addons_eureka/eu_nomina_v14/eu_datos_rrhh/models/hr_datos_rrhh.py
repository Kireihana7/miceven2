# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import (datetime,date)
from dateutil import (relativedelta)
import re

_logger = logging.getLogger(__name__)
_DATETIME_FORMAT = "%Y-%m-%d"

class Employee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee antiguedad'

    TIPO_CUENTA = [
        ('0', 'Corriente'),
        ('1', 'Ahorro'),
    ]

    # Datos para Antiguedad 
    fecha_inicio = fields.Date("Fecha de Ingreso", required=True)
    fecha_fin = fields.Date("Fecha de Egreso")
    dias_antig = fields.Integer('Dias', help="Total de dias de Antiguedad.", compute="compute_fecha_ingreso", )
    mes_antig = fields.Integer('Mes', help="Total de Meses de Antiguedad.", compute="compute_fecha_ingreso", )
    ano_antig = fields.Integer('Año', help="Total de Años de Antiguedad.", compute="compute_fecha_ingreso", )
    m_egreso = fields.Many2one('hr.egress.conditions','Motivo de Egreso')
    bank_account_id_emp_2 = fields.Many2one('res.bank', 'Banco de Nomina', help="Payslip bank")
    account_number_2 = fields.Char('Nro. de Cuenta', size=20)
    account_type_2 = fields.Selection(TIPO_CUENTA, 'Tipo de Cuenta')

    _sql_constraints = [
        ('uniq_account_number_2', 'UNIQUE(x_account_number_2)',
         "El numero de cuenta ya esta registrado! Debe indicar otro."),
    ]

    # Calculo y validacion de los dias de antiguedad
    @api.depends('fecha_inicio')
    def compute_fecha_ingreso(self):
        for rec in self:
            rec.dias_antig = 0
            rec.mes_antig = 0
            rec.ano_antig = 0
            fecha = rec.fecha_inicio
            if fecha:
                age = rec.calcular_antiguedad(fecha)
                if age['days'] >= 0 and age['months'] >= 0 and age['years'] >= 0:
                    rec.dias_antig = age['days']
                    rec.mes_antig = age['months']
                    rec.ano_antig = age['years']
                else:
                    rec.dias_antig = False
                    rec.mes_antig = False
                    rec.ano_antig = False
                    return {
                        'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    @api.onchange('account_number_2')
    def onchange_account_number(self):
        if self.account_number_2:
            res = self.validate_number(self.account_number_2)
            if not res:
                # self.account_number = ''
                return {'warning': {'title': "Advertencia!",
                                    'message': u'El número de cuenta tiene el formato incorrecto. Ej: 01234567890123456789. Por favor intente de nuevo'}}

    def validate_number(self, number):
        res = {}
        number_obj = re.compile(r"""^\d{20}""", re.X)

        if number_obj.search(number):
            res = {
                'valor': number
            }
        return res

    def calcular_antiguedad(self, fecha):
        res = {}
        ahora = date.today()
        if fecha:
            diferencia = relativedelta.relativedelta(ahora,fecha )
            res.update({'years': diferencia.years})
            res.update({'months': diferencia.months})
            res.update({'days': diferencia.days})
            # self.write(res)
        return res

    def actualizar_antiguedad(self, cr, uid):
        print("====Inicio Cambio de antiguedad====")
        employee_ids = self.search(cr, uid, [])
        employees = self.browse(cr, uid, employee_ids)
        values = {}
        res = {}
        ahora = datetime.now().strftime(_DATETIME_FORMAT)
        for emp in employees:
            fecha = emp.fecha_inicio
            if fecha:
                diferencia = relativedelta.relativedelta(datetime.strptime(ahora, _DATETIME_FORMAT),
                                                         datetime.strptime(fecha, _DATETIME_FORMAT))
                res.update({'ano_antig': diferencia.years})
                res.update({'mes_antig': diferencia.months})
                res.update({'dias_antig': diferencia.days})
                self.write(cr, uid, emp.id, res)
        print("====Cambio de nombres Ejecutado====")

    def write(self, values):
        acc_num = values.get('account_number_2', False)
        if acc_num:
            res = self.validate_number(acc_num)
            if not res:
                self.account_number_2 = ''
                raise Warning(
                    u'El número de cuenta tiene el formato incorrecto. Ej: 01234567890123456789. Por favor intente de nuevo')
        res = super(Employee, self).write(values)
        return res

    @api.model
    def create(self, values):
        acc_num = values.get('account_number_2', False)
        if acc_num:
            res = self.validate_number(acc_num)
            if not res:
                raise UserError('El número de cuenta tiene el formato incorrecto. Ej: 01234567890123456789. Por favor intente de nuevo')
        wh_iva_id = super(Employee, self).create(values)
        return wh_iva_id


class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    _description = 'Employee antiguedad'

    TIPO_CUENTA = [
        ('0', 'Corriente'),
        ('1', 'Ahorro'),
    ]

    # Datos para Antiguedad 
    fecha_inicio = fields.Date("Fecha de Ingreso", required=True)
    fecha_fin = fields.Date("Fecha de Egreso")
    dias_antig = fields.Integer('Dias', help="Total de dias de Antiguedad.", compute="compute_fecha_ingreso", )
    mes_antig = fields.Integer('Mes', help="Total de Meses de Antiguedad.", compute="compute_fecha_ingreso", )
    ano_antig = fields.Integer('Año', help="Total de Años de Antiguedad.", compute="compute_fecha_ingreso", )
    m_egreso = fields.Many2one('hr.egress.conditions','Motivo de Egreso')
    m_egreso = fields.Many2one('hr.egress.conditions','Motivo de Egreso')
    bank_account_id_emp_2 = fields.Many2one('res.bank', 'Banco de Nomina', help="Payslip bank")
    account_number_2 = fields.Char('Nro. de Cuenta', size=20)
    account_type_2 = fields.Selection(TIPO_CUENTA, 'Tipo de Cuenta')

    @api.depends('fecha_inicio')
    def compute_fecha_ingreso(self):
        for rec in self:
            rec.dias_antig = 0
            rec.mes_antig = 0
            rec.ano_antig = 0
            fecha = rec.fecha_inicio
            if fecha:
                age = rec.calcular_antiguedad(fecha)
                if age['days'] >= 0 and age['months'] >= 0 and age['years'] >= 0:
                    rec.dias_antig = age['days']
                    rec.mes_antig = age['months']
                    rec.ano_antig = age['years']
                else:
                    rec.dias_antig = False
                    rec.mes_antig = False
                    rec.ano_antig = False
                    return {
                        'warning': {'title': "Advertencia!", 'message': "La fecha ingresada es mayor que la fecha actual"}}

    def calcular_antiguedad(self, fecha):
        res = {}
        ahora = date.today()
        if fecha:
            diferencia = relativedelta.relativedelta(ahora,fecha )
            res.update({'years': diferencia.years})
            res.update({'months': diferencia.months})
            res.update({'days': diferencia.days})
            # self.write(res)
        return res