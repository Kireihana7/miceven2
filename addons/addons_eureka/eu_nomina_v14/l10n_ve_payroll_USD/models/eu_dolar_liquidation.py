# -*- coding: utf-8 -*-

from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from math import floor
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, timedelta,date
from calendar import monthrange

TODAY=datetime.today()

class HRLiquidacion(models.Model):
    _inherit = 'hr.liquidacion'

    # @api.depends("employee_id","fecha")
    # def _get_sal_diario(self):
    #     for rec in self:
    #             if rec.vacation_payslip:
    #                 nominas=rec.env['hr.payslip'].search([('is_anihilation','=',False),('employee_id','=',rec.employee_id.id)]).filtered(lambda x:x.date_to.month==rec.fecha.month and x.id!=rec.vacation_payslip.id)
    #             else:
    #                 nominas=rec.env['hr.payslip'].search([('is_anihilation','=',False),('employee_id','=',rec.employee_id.id)]).filtered(lambda x:x.date_to.month==rec.fecha.month)
    #             total=sum(x.total_usd  for x in nominas.mapped("line_ids").filtered(lambda x: x.category_id.code=="BASIC"))

    #             contrato=rec.employee_id.contract_id #obtenido contrato
    #             if total<contrato.wage:
    #                 sal_mensual=contrato.wage
    #             else:
    #                 sal_mensual=total #obtenido sal_mensual
    #             sal_diario=sal_mensual/30 #obtenido sal_diario
    #             rec.alicuota_utilidades=(sal_diario*rec.env.company.cant_dias_utilidades)/360 #obtenido utilidades 
    #             dias_vacaciones=rec.env.company.dias_vac_base + rec.employee_id.dias_bono
    #             rec.alicuota_vacaciones=(sal_diario*dias_vacaciones)/360 #obtenido vacaciones
    #             sal_dia_total=sal_diario+rec.alicuota_vacaciones+rec.alicuota_utilidades #tenemos diario integral
    #             if sal_dia_total<1:
    #                 rec.sal_diario=rec.contract_id.wage/30
    #             else:
    #                 rec.sal_diario=round(sal_dia_total,2)