# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta

TODAY=date.today()

class HrEmployeeJourneyGr(models.Model):
    _name = 'hr.employee.journey.group'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active=fields.Boolean(string="Activo",default=True,tracking=True)
    name=fields.Char("Nombre del grupo",tracking=True)
    employee_ids=fields.Many2many('hr.employee',string="empleados del grupo",tracking=True)
    sequence=fields.Integer("secuencia",tracking=True)
    categoria=fields.Many2one('journey_group_categ',tracking=True)
    schedule_id=fields.Many2one('resource.calendar',tracking=True)
    rotation_days=fields.Integer('Dias para rotación',related="categoria.rotation_days")
    company_id=fields.Many2one(default=lambda self: self.env.company)

    def change_contract_schedule(self):
        for rec in self:
            if rec.employee_ids and rec.schedule_id:
                for e in rec.employee_ids:
                    today= fields.Datetime.now()

                    work_entries = self.env['hr.work.entry'].search([('date_start', '>', today ),('employee_id', '=', e.id),('company_id', '=', rec.company_id.id)])
                    for w in work_entries:
                        w.sudo().unlink()
                    if e.contract_id:
                        e.contract_id.resource_calendar_id=rec.schedule_id
                        e.resource_calendar_id=rec.schedule_id
                        if e.contract_id.date_end:
                            e.contract_id._generate_work_entries(today.date(),e.contract_id.date_end)
                        elif rec.rotation_days>0:
                            e.contract_id.generate_and_change_entries(today, today+relativedelta(days=rec.rotation_days))
                        else:
                            e.contract_id.generate_and_change_entries(today, today+relativedelta(days=360))

class HrJourneyGroupCategory(models.Model):
    _name="journey_group_categ"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string="Nombre",tracking=True)
    code=fields.Char("Código",tracking=True)
    groups_ids=fields.One2many('hr.employee.journey.group','categoria',string="grupos relacionados",tracking=True)
    rotation_days=fields.Integer('Dias para rotación',tracking=True)
