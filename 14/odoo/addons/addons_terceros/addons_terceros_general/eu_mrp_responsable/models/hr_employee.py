# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'


    reponsable_quality = fields.Boolean(string='Responsable de Control de calidad',default=False)
    reponsable_production = fields.Boolean(string='Responsable de Producción',default=False)
    reponsable_pcp = fields.Boolean(string='Responsable de PCP',default=False)
    reponsable_romana = fields.Boolean(string='Responsable de Romana',default=False)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    reponsable_quality = fields.Boolean(string='Responsable de Control de calidad',default=False)
    reponsable_production = fields.Boolean(string='Responsable de Producción',default=False)
    reponsable_pcp = fields.Boolean(string='Responsable de PCP',default=False)
    reponsable_romana = fields.Boolean(string='Responsable de Romana',default=False)
