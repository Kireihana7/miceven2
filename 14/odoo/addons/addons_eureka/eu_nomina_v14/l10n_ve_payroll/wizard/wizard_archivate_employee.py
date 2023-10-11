# -*- coding: utf-8 -*-


from odoo import fields, models,api
from odoo.exceptions import UserError
from datetime import date,datetime
from calendar import monthrange,monthcalendar,setfirstweekday
TODAY = date.today()


class HrDepartureWizard(models.TransientModel):

    _inherit="hr.departure.wizard"

    def action_register_departure(self):
        res=super().action_register_departure()
        employee = self.employee_id
        employee.fecha_fin=self.departure_date
        return res