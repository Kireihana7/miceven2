# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta
from calendar import monthrange


class HrWizJourneys(models.TransientModel):
    _name="hr.wiz.journeys"

    date_today=fields.Date("Fecha")

    def print_report(self):
        
        
        return self.env.ref('eu_payslip_corporate_view.action_report_hr_wiz_journeys').report_action(self)
        