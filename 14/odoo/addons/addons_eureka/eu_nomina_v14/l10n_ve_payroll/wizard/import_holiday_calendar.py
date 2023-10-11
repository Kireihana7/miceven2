# -*- coding: utf-8 -*-

from odoo import fields, models,api
from odoo.exceptions import UserError
from datetime import date,datetime
from calendar import monthrange
import base64
import csv
import io
TODAY = date.today()


class ImportHolidayCalendarWizard(models.TransientModel):
    _name = 'import.holiday.calendar.wizard'
    _description = 'sube los dias feriados mediante csv'

    
    archivo =fields.Binary( string="Archivo CSV",required=True)
    delimiter=fields.Char(string="Delimitador",limit=1)
        
    
    def create_entries(self):
        for rec in self:
            csv_data = base64.b64decode(rec.archivo)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            readCSV = list(csv.reader(data_file, delimiter=rec.delimiter))
            holiday_obj=self.env['hr.holidays.per.year.line']
            for row in readCSV:
                
                holiday_obj.create({
                    'parent_id':self.env.context.get('parent', False),
                    'name':row[0],
                    'fecha':datetime.strptime(row[1],'%d/%m/%Y')
                })