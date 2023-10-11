# -*- coding: utf-8 -*-

from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from calendar import monthrange,weekday
from odoo import models, fields,api
from odoo.exceptions import UserError
class EuHrstrcut(models.Model):
    _inherit="hr.payroll.structure"
    
    corporate_type=fields.Boolean(string="guardar en vista corporativa")
    its_super_secret=fields.Boolean(string="Shh", groups="eu_payslip_corporate_view.corporate_super_payslip_group")

class EuHRPayslipRun(models.Model):
    _inherit="hr.payslip.run"
    
    its_super_secret=fields.Boolean(string="Shh", groups="eu_payslip_corporate_view.corporate_super_payslip_group")
    corporate_type=fields.Boolean(string="guardar en vista corporativa")

class EuHRContract(models.Model):
    _inherit="hr.contract"
    
    its_super_secret_salary=fields.Boolean(string="Salario Corporativo", groups="eu_payslip_corporate_view.corporate_super_payslip_group")

class EuHRPayslip(models.Model):
    _inherit="hr.payslip"
    its_super_secret=fields.Boolean(string="Shh", groups="eu_payslip_corporate_view.corporate_super_payslip_group" ,related="struct_id.its_super_secret")
    corporate_type=fields.Boolean(string="guardar en vista corporativa", related="struct_id.corporate_type")
    liquidation_corporate=fields.Many2one('hr.liquidacion.corporate')
# Si le colocamos como tipo de estructuras utilidades, entonces no se tomaran en cuenta en ningun lado salvo, no se donde pueda me parece que nada

    @api.depends('date_from','date_to')
    @api.constrains("employee_id")
    def _payslip_duplicated_by_date(self):
        for rec in self:
            if self.env['hr.payslip'].search([('state','not in',['cancel']),('corporate_type','!=',True),('employee_id','=',rec.employee_id.id),('date_from','=',rec.date_from),('date_to','=',rec.date_to),('company_id','=',rec.env.company.id),('id','!=',rec.id),('struct_id','=',rec.struct_id.id)]):
                raise UserError("Ya existe una nómina para este empleado en este periodo, si no la visualiza. haga click en 'Todas las nominas' ")
    @api.constrains("anno_vacaciones_designado")
    def _cosntrain_anno_vacacion_designate(self):
        for rec in self:
            if rec.liquidation_id or rec.liquidation_corporate:
                pass
            elif rec.employee_id.fecha_inicio and rec.is_vacation and rec.anno_vacaciones_designado<=rec.employee_id.fecha_inicio.year:
                raise UserError(f"Este no es un año valido para las vacaciones del empleado {rec.employee_id.name}")
            else:
                pass
    @api.constrains('employee_id')
    def _constrain_vacaciones(self):
        for rec in self:
            if rec.is_vacation and not rec.liquidation_id and not rec.corporate_type:
                vacaciones=rec.env['hr.payslip'].search([('state','not in',['cancel']),('employee_id','=',rec.employee_id.id),('is_vacation','=',True),('id','!=',rec.id)])
                if len(vacaciones)>rec.employee_id.vacaciones_total:
                    raise UserError("Este individuo ya a usado todas sus vacaciones disponibles")
                if vacaciones.filtered(lambda x: x.id !=rec.id and x.anno_vacaciones_designado==rec.anno_vacaciones_designado):
                    raise UserError("Ya este trabajador "+rec.employee_id.name+" presenta vacaciones para el año "+str(rec.anno_vacaciones_designado))

