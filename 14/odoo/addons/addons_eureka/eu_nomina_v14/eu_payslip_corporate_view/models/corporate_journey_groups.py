# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta
from calendar import monthrange


TODAY=date.today()
class HrEmployeeJourneyGr(models.Model):
    _inherit = 'hr.employee.journey.group'

    its_secret_journey=fields.Boolean("Corporativa")    
    def change_contract_schedule(self):
        for rec in self:
            if rec.its_secret_journey:
                if rec.employee_ids and rec.schedule_id:
                    for e in rec.employee_ids:
                        today= fields.Datetime.now()

                        if e.secret_journey:
                            e.secret_journey=rec.schedule_id
            else:
                super().change_contract_schedule()
class HrJourneyGroupCategory(models.Model):
    _inherit="journey_group_categ"

    its_secret_journey=fields.Boolean("Corporativa")
    name=fields.Char(string="Nombre",tracking=True)
    code=fields.Char("Código",tracking=True)
    groups_ids=fields.One2many('hr.employee.journey.group','categoria',string="grupos relacionados",tracking=True)
    rotation_days=fields.Integer('Dias para rotación',tracking=True)
