# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models,fields,api
from datetime import datetime, timedelta,date
from calendar import monthrange,weekday
import locale


class HrWorkEntry(models.Model):
    _name = 'hr.work.entry'
    _inherit = ['hr.work.entry','mail.thread', 'mail.activity.mixin']

    feriado_laborado_date_start=fields.Boolean("feriado laborado",compute="_compute_dias_feriados_laborados",store=True)
    feriado_laborado_date_end=fields.Boolean("feriado laborado",compute="_compute_dias_feriados_laborados",store=True)
    feriados_libre_laborado_date_start=fields.Boolean("feriado libre laborado",compute="_compute_dias_feriados_laborados",store=True)
    feriados_libre_laborado_date_end=fields.Boolean("feriado libre laborado",compute="_compute_dias_feriados_laborados",store=True)
    horas_feriadas_laboradas_date_start=fields.Float("horas feriadas laboradas dia inicial",store=True,compute="_compute_dias_feriados_laborados")
    horas_feriadas_laboradas_date_end=fields.Float("horas feriadas laboradas dia final",store=True,compute="_compute_dias_feriados_laborados")
    horas_feriadas_totales=fields.Float("horas feriadas",store=True,compute="_compute_dias_feriados_laborados")
    aux=fields.Boolean(compute="_compute_dias_feriados_laborados")
    @api.depends('employee_id','date_start','date_stop','work_entry_type_id','duration')
    def _compute_dias_feriados_laborados(self):
        for rec in self:
            rec.feriado_laborado_date_start=False
            rec.feriado_laborado_date_end=False
            rec.feriados_libre_laborado_date_start=False
            rec.horas_feriadas_laboradas_date_start=0
            rec.horas_feriadas_laboradas_date_end=0
            rec.horas_feriadas_totales=0
            if rec.employee_id and rec.work_entry_type_id.code=="WORK100":
                rec.horas_feriadas_totales=0
                # definimos nuestras variables de trabajo
                contract=rec.employee_id.contract_id
                work_calendar=contract.resource_calendar_id
                holidays_calendar= self.env['hr.holidays.per.year'].search([('anno_abo','=',rec.date_stop.year)],order='id desc', limit=1)
                is_weekday_start=weekday(fields.Datetime.context_timestamp(rec,rec.date_start).year, fields.Datetime.context_timestamp(rec,rec.date_start).month, fields.Datetime.context_timestamp(rec,rec.date_start).day)
                is_weekday_stop=weekday(fields.Datetime.context_timestamp(rec,rec.date_stop).year, fields.Datetime.context_timestamp(rec,rec.date_stop).month, fields.Datetime.context_timestamp(rec,rec.date_stop).day)
                worked_day_start=work_calendar.attendance_ids.filtered(lambda x : int(x.dayofweek)==int(is_weekday_start) and is_weekday_start!=6 )
                worked_day_stop=work_calendar.attendance_ids.filtered(lambda x : int(x.dayofweek)==int(is_weekday_stop) and is_weekday_stop!=6 )
                check_day_start=work_calendar.attendance_ids.filtered(lambda x : int(x.dayofweek)==int(is_weekday_start) and x.check_count)
                check_day_stop=work_calendar.attendance_ids.filtered(lambda x : int(x.dayofweek)==int(is_weekday_stop) and x.check_count)

                #Si todo esta en un mismo dia como deberia ser
                if fields.Datetime.context_timestamp(rec,rec.date_start).date()==fields.Datetime.context_timestamp(rec,rec.date_stop).date():
                    holiday=holidays_calendar.holidays_lines_ids.filtered(lambda x: x.fecha==fields.Datetime.context_timestamp(rec,rec.date_start).date())
                    #buscamos si es dia feriado
                    is_weekday=weekday(fields.Datetime.context_timestamp(rec,rec.date_start).year, fields.Datetime.context_timestamp(rec,rec.date_start).month, fields.Datetime.context_timestamp(rec,rec.date_start).day)
                    worked_day=work_calendar.attendance_ids.filtered(lambda x : int(x.dayofweek)==int(is_weekday) and int(x.dayofweek)!=6 and x.check_count)
                    #buscamos si ese dia se labora
                    if holiday and (not worked_day):
                        rec.feriados_libre_laborado_date_start=True
                        rec.horas_feriadas_laboradas_date_start=0
                        rec.horas_feriadas_laboradas_date_end=0
                        rec.horas_feriadas_totales=rec.duration
                    elif (holiday and  worked_day) or (not holiday and not worked_day):
                        rec.feriado_laborado_date_start=True
                        rec.horas_feriadas_laboradas_date_start=0
                        rec.horas_feriadas_laboradas_date_end=0
                        rec.horas_feriadas_totales=rec.duration
                    else:
                        
                        rec.horas_feriadas_laboradas_date_start=0
                        rec.horas_feriadas_laboradas_date_end=0
                        rec.horas_feriadas_totales=0
                #en caso contrario porque son cabrones
                
                elif check_day_start and not check_day_stop:
                    holiday=holidays_calendar.holidays_lines_ids.filtered(lambda x: x.fecha==fields.Datetime.context_timestamp(rec,rec.date_start).date())
                    
                    if holiday and not worked_day_start:
                            rec.feriados_libre_laborado_date_start=True

                            rec.horas_feriadas_laboradas_date_start=rec.duration
                            
                            
                    elif (holiday and  worked_day_start) or (not holiday and not worked_day_start):
                            rec.feriado_laborado_date_start=True

                            rec.horas_feriadas_laboradas_date_start=rec.duration
                    else:
                            pass
                    
                else:
                    holiday=holidays_calendar.holidays_lines_ids.filtered(lambda x: x.fecha==fields.Datetime.context_timestamp(rec,rec.date_start).date() or x.fecha==fields.Datetime.context_timestamp(rec,rec.date_stop).date())

                    if holiday and fields.Datetime.context_timestamp(rec,rec.date_start).date() in holiday.mapped('fecha'):


                        if holiday and not worked_day_start:
                            rec.feriados_libre_laborado_date_start=True
                            if fields.Datetime.context_timestamp(rec,rec.date_start).hour <13:
                                rec.horas_feriadas_laboradas_date_start=24-fields.Datetime.context_timestamp(rec,rec.date_start).hour
                            else:
                                rec.horas_feriadas_laboradas_date_start=fields.Datetime.context_timestamp(rec,rec.date_start).hour
                            
                            
                        elif (holiday and  worked_day_start) or (not holiday and not worked_day_start):
                            rec.feriado_laborado_date_start=True
                            if fields.Datetime.context_timestamp(rec,rec.date_start).hour <13:
                                rec.horas_feriadas_laboradas_date_start=24-fields.Datetime.context_timestamp(rec,rec.date_start).hour
                            else:
                                rec.horas_feriadas_laboradas_date_start=fields.Datetime.context_timestamp(rec,rec.date_start).hour 
                        else:
                            pass
                    elif not holiday and not worked_day_start:
                        rec.feriado_laborado_date_start=True
                        if fields.Datetime.context_timestamp(rec,rec.date_start).hour <13:
                            rec.horas_feriadas_laboradas_date_start=24-fields.Datetime.context_timestamp(rec,rec.date_start).hour
                        else:
                            rec.horas_feriadas_laboradas_date_start=fields.Datetime.context_timestamp(rec,rec.date_start).hour 
                    
                    elif holiday and fields.Datetime.context_timestamp(rec,rec.date_stop).date() in holiday.mapped('fecha'):

                            if holiday and not worked_day_stop:
                                rec.feriados_libre_laborado_date_end=True
                                if fields.Datetime.context_timestamp(rec,rec.date_stop).hour <13:
                                    rec.horas_feriadas_laboradas_date_end=fields.Datetime.context_timestamp(rec,rec.date_stop).hour
                                else:
                                    rec.horas_feriadas_laboradas_date_end=24-fields.Datetime.context_timestamp(rec,rec.date_stop).hour

                            elif (holiday and  worked_day_stop) or (not holiday and not worked_day_stop):
                                rec.feriado_laborado_date_end=True
                                if fields.Datetime.context_timestamp(rec,rec.date_stop).hour <13:
                                    rec.horas_feriadas_laboradas_date_end=fields.Datetime.context_timestamp(rec,rec.date_stop).hour
                                else:
                                    rec.horas_feriadas_laboradas_date_end=24-fields.Datetime.context_timestamp(rec,rec.date_stop).hour
                            else:
                                pass
                    elif not holiday and not worked_day_stop and contract.resource_calendar_id.hours_per_day<16:
                        rec.feriado_laborado_date_end=True
                        if fields.Datetime.context_timestamp(rec,rec.date_stop).hour <13:
                            rec.horas_feriadas_laboradas_date_end=24-fields.Datetime.context_timestamp(rec,rec.date_stop).hour
                        else:
                            rec.horas_feriadas_laboradas_date_end=fields.Datetime.context_timestamp(rec,rec.date_stop).hour
                    else:
                        pass
            rec.aux=True
    def recalcular(self):
        for rec in self:
            rec._onchange_contract_id()
            rec._compute_dias_feriados_laborados()
# ACA COLOCAREMOS LA LOGICA PARA QUE LAS ASISTENCIAS DEL MODULO SE AGREGUEN A LAS ENTRADAS DE TRABAJO
    @api.model
    def create(self,vals):
        work_entries = super().create(vals)
        # if work_entries._check_if_error():
        #     raise UserError ("La entrada que intenta crear es conflictiva o el tipo de entrada presenta fallos")
        return work_entries

class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    is_reposo=fields.Boolean("Es Reposo")


class HrAttendanceRemax(models.AbstractModel):
    _inherit="hr.employee.base"


    def create_work_entry_from_attendance(self,attendance):
         if attendance.check_out !=False and self.env['ir.config_parameter'].sudo().get_param('l10n_ve_payroll.create_work_entry_with_attendance'):
            entrace=self.env['hr.work.entry'].sudo().create({
                'name':f"Asistencia : {attendance.employee_id.name}",
                'employee_id':attendance.employee_id.id,
                'date_start':attendance.check_in,
                'date_stop':attendance.check_out,
                'duration':attendance.worked_hours,
                'work_entry_type_id':self.env['hr.work.entry.type'].search([('code','=','WORK100')],limit=1).id
            })
            entrace._compute_dias_feriados_laborados()

    def _attendance_action_change(self):
        attendance=super()._attendance_action_change()
        self.create_work_entry_from_attendance(attendance)
        return attendance