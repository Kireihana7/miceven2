# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta
from .test import scrap_from_BCV_Prestaciones
from calendar import monthrange


class HrJob(models.Model):
    _inherit = 'hr.job'

    code=fields.Char("Codigo")
    