# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    delay_hours = fields.Float(string="Tiempo de retraso")
    early_leave_hours=fields.Float(string="Tiempo no cumplido")
    department=fields.Many2one('hr.department',compute="_compute_department")

    @api.depends('employee_id','employee_id.department_id')
    def _compute_department(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.department_id:
                rec.department=rec.employee_id.department_id
            else:
                rec.department=False

    