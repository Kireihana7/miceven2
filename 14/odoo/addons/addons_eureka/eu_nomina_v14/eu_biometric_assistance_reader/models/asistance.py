# -*- coding: utf-8 -*-

from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from calendar import monthrange,weekday
from odoo import models, fields,api
from odoo.exceptions import UserError

class HrAttendance(models.Model):
    _inherit="hr.attendance"

    delay_hours=fields.Integer("Horas de retraso")
    