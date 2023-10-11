# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta
from calendar import monthrange


TODAY=date.today()
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    even_odd_week=fields.Selection([('even','even'),('odd','odd')],string="Even or Odd")
    day=fields.Integer('weekday')
    date=fields.Date('fecha')
    feriado=fields.Boolean("Dia feriado")

    def _get_calendario_feriado(self):
        for rec in self:
            thisdateyear=rec.date.year
            thisyear=TODAY.year
            if self.env['hr.holidays.per.year'].search([('anno_abo','=',thisdateyear)],order='id desc', limit=1):
                return self.env['hr.holidays.per.year'].search([('anno_abo','=',thisdateyear)],order='id desc', limit=1)
            else:
                return self.env['hr.holidays.per.year'].search([('anno_abo','=',thisyear)],order='id desc', limit=1)
    def check_times(self):
        for rec in self:
            rec.day=fields.Datetime.context_timestamp(rec,rec.check_in).weekday()
            rec.date=fields.Datetime.context_timestamp(rec,rec.check_in).date()
            if rec.employee_id.secret_journey:
                # buscamos el periodo en el que nos encontramos
                previous=self.env['hr.attendance'].search([('day','=',rec.day),('date','<',rec.date),('employee_id','=',rec.employee_id.id)],order="id desc",limit=1)
                if previous.even_odd_week=="even" and (rec.date - fields.Datetime.context_timestamp(previous,previous.date)).days>10:
                    rec.even_odd_week=="even"
                elif previous.even_odd_week=="odd" and (rec.date - fields.Datetime.context_timestamp(previous,previous.date)).days>10:
                    rec.even_odd_week=="odd"
                elif previous.even_odd_week=="even":
                    rec.even_odd_week=="odd"
                else:
                    rec.even_odd_week="even"
                tipo= "1" if rec.even_odd_week=="odd" else "0"
                horarioshoy=rec.employee_id.secret_journey.attendance_ids.filtered(lambda x:x.dayofweek==str(rec.day) and x.week_type==tipo and x.check_count)
                horariohoy=horarioshoy
                if len(horarioshoy)>1:
                    tiempodia='morning' if fields.Datetime.context_timestamp(rec,rec.check_in).hour<12 else 'afternoon'
                    horariohoy=horarioshoy.filtered(lambda x: x.day_period==tiempodia)
                    
                # Obtenemos las diferencias horarias entre las fechas de entrada
                if horariohoy:
                    dif_hours=fields.Datetime.context_timestamp(rec,rec.check_in).hour-horariohoy.hour_from
                    delay=int(dif_hours)
                    rec.delay_hours=delay
                if rec.check_out:
                # Obtenemos las diferencias horarias entre las fechas de salida
                    difa_hours=horariohoy.hour_to-fields.Datetime.context_timestamp(rec,rec.check_out).hour
                    earliness=int(difa_hours)
                    rec.early_leave_hours=earliness

    def check_feriado(self):
        calendario=self._get_calendario_feriado()
        for rec in self:
            if rec.date in calendario.holidays_lines_ids.mapped("fecha"):
                rec.feriado=True
            else:
                rec.feriado=False
        
    @api.model
    def create(self,vals):
        res=super().create(vals)
        res.check_times()
        res.check_feriado()

        return res
    def write(self,vals):
        res=super().write(vals)
        if any([vals.get('check_out'),vals.get('check_in')]):
            self.check_times()
            self.check_feriado()
        return res


