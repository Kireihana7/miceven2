# -*- coding: utf-8 -*-
#flagship----aqui cambiamos el calculo del emonto en ingles
from odoo.exceptions import UserError
from odoo import models, fields,api
from datetime import datetime, timedelta,date
from calendar import monthrange
import locale

from .test import scrap_from_publicholidays_ve
TODAY=date.today()
MONTH_LIST={'enero':'01','febrero':'02','marzo':'03','abril':'04','mayo':'05','junio':'06','julio':'07','agosto':'08','septiembre':'09','octubre':'10','noviembre':'11','diciembre':'12'}

class HRHolidaysPerYear(models.Model):
    _name = 'hr.holidays.per.year'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string="feriados para:")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company.id,tracking=True,invisible=True)
    holidays_lines_ids=fields.One2many('hr.holidays.per.year.line','parent_id',tracking=True)
    anno=fields.Date("Año",default=date.today(),readonly=True,tracking=True)
    anno_abo=fields.Integer(compute="get_year",store=True)

    def generate_work_entries47(self):
        time=datetime.combine(self.anno,datetime.min.time())
        begin=time.replace(day=1,month=1)
        end=time.replace(day=1,month=1,year=time.year+1)
        entradas=self.env['hr.work.entry'].search([('date_start','>=',begin),('date_stop','<',end)])
        
        employees=self.env['hr.employee'].search([()])
        if employees:
            current_contracts = employees._get_contracts(begin.date(), end.date() , states=['open', 'close'])
        else:
            current_contracts = employees._get_all_contracts(begin.date(), end.date(), states=['open', 'close'])

        employees.contract_id._generate_work_entries(begin.date(), end.date())
           


    @api.depends('anno')
    def get_year(self):
        for rec in self:
            rec.anno_abo=rec.anno.year
    @api.model
    def create(self,vals):
        res=super().create(vals)

        res.name=str(res.anno.year)+" Días Feriados"
        return res
    @api.constrains('anno')
    def constrain_year(self):
        for rec in self:
            if not rec.anno:
                raise UserError("Ingrese un año para esta entrada")
            # elif rec.env['hr.holidays.per.year'].search([('anno.year','=',rec.anno.year)]):
            #     raise UserError("Ya existe una entrada para este año")

    def load_from_web(self):
        for rec in self:
            try:
                raw_data=scrap_from_publicholidays_ve(self)
                
            except:
                raise UserError("A ocurrido un error, porfavor revise su conexion a internet o carge los dias de mediante otra opcion")
           
            for line in raw_data:

                #buscamos la fecha
                if line[0]:
                    dia_mes=line[0].split(" ")

                    datetime_object = datetime.strptime(str(dia_mes[0])+" "+MONTH_LIST.get(dia_mes[1])+" "+str(TODAY.year),"%d %m %Y")
                    rec.holidays_lines_ids+=rec.env['hr.holidays.per.year.line'].create({
                    'parent_id':rec.id,
                    'name': line[2],
                    'fecha':datetime_object
                    })
                else:
                   pass
                

    def load_from_document(self):
        for rec in self:
            return {
                        'type':'ir.actions.act_window',
                        'res_model':'import.holiday.calendar.wizard',
                        'view_mode':'form',
                        'target':'new',
                        'context':{'parent':rec.id},
                        'binding_model_id':False,
                    } 
class HRHolidaysPerYearLine(models.Model):
    _name = 'hr.holidays.per.year.line'

    parent_id=fields.Many2one('hr.holidays.per.year')

    name=fields.Char("Nombre feriado")
    fecha=fields.Date("Fecha")