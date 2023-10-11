# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _,exceptions
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee disability"

    auditiva    =   field_name = fields.Boolean(string='auditiva',)
    intelectual =   field_name = fields.Boolean(string='intelectual',)
    mental      =   field_name = fields.Boolean(string='mental',)
    muscular    =   field_name = fields.Boolean(string='muscular',)
    visual       =   field_name = fields.Boolean(string='visual',)
    otro        =   field_name = fields.Boolean(string='otro',)

    discapacidad_employe_descripcion = fields.Char(string='Descripcion Discapacidad')   

class EmployeePublic(models.Model):
    _inherit = "hr.employee.public"
    _description = "Employee disability"

    auditiva    =   field_name = fields.Boolean(string='auditiva',)
    intelectual =   field_name = fields.Boolean(string='intelectual',)
    mental      =   field_name = fields.Boolean(string='mental',)
    muscular    =   field_name = fields.Boolean(string='muscular',)
    visual       =   field_name = fields.Boolean(string='visual',)
    otro        =   field_name = fields.Boolean(string='otro',)

    discapacidad_employe_descripcion = fields.Char(string='Descripcion Discapacidad')