
from odoo import fields, models, _, exceptions, api
# importando el modulo de regex de python
import re
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta

_DATETIME_FORMAT = "%Y-%m-%d"

class HRDepartment(models.Model):
    _inherit='hr.department'
    cost_center=fields.Many2one('account.analytic.account',string="Centro de costo")
    jefe_id=fields.Many2one('hr.employee',string="Jefe de Departamento")

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = "hr.employee"


    cost_center=fields.Many2one('account.analytic.account',string="Centro de costo")

class HrEmployeeP(models.Model):
    _name = 'hr.employee.public'
    _inherit = "hr.employee.public"


    cost_center=fields.Many2one('account.analytic.account',string="Centro de costo")

class Job(models.Model):

    _inherit = "hr.job"
    
    # @api.model
    # def create(self,vals):
    #     res=super().create(vals)

    #     for rec in res:
    #         if not rec.cost_center:
    #             rec.cost_center=self.env['account.analytic.account'].create({
    #                 'name':rec.name+'-centro de costo',
    #                 'company_id':rec.company_id.id,
    #             })
                
    #     return res
    cost_center=fields.Many2one('account.analytic.account',string="Centro de costo")
