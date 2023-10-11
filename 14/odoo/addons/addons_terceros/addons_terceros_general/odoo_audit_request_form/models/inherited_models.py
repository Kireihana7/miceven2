# -*- coding: utf-8 -*-

from odoo import fields, models

class HrDepartment(models.Model):
    _inherit = "hr.department"

    is_audit_department = fields.Boolean("Departamento de auditoría", tracking=True,)