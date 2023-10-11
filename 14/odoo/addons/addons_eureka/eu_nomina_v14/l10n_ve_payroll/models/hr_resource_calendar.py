# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta,date

TODAY=date.today()

class HrResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    check_count=fields.Boolean(string="Considera",default=True)

class HrResourceCalendar(models.Model):
    _name = 'resource.calendar'
    _inherit = ['resource.calendar','mail.thread', 'mail.activity.mixin']
    attendance_ids=fields.One2many('resource.calendar.attendance','calendar_id',tracking=True)
    hours_per_day = fields.Float(tracking=True)
    tz = fields.Selection(tracking=True)    
    full_time_required_hours = fields.Float(tracking=True)
    work_time_rate = fields.Float(tracking=True)
    check_jornada_diurna=fields.Boolean(string="Jornada diurna")
    check_jornada_nocturna=fields.Boolean(string="Jornada nocturna")
    check_jornada_mixta=fields.Boolean(string="Jornada mixta")
    rest_days=fields.Integer(string="Dias de descanso")
    interjournal_rest=fields.Integer(string="Horas de descanso interjornada")