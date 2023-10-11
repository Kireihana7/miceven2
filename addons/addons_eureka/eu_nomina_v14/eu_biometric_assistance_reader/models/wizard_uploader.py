# -*- coding: utf-8 -*-

from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from calendar import monthrange,weekday
from odoo import models, fields,api,_
from odoo.exceptions import UserError
import xlrd
import base64
import re
import io
import tempfile
import binascii
class EuHrstrcut(models.TransientModel):
    _name="hr.biometric.upload.wiz"
    
    archive_to_upload=fields.Binary(string="Porfavor cargue su archivo")

    def excel_to_python(self,archive):
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(archive))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        return workbook
    def digitalized(self):
        if self.archive_to_upload:
            # ids_values
            workbook = self.excel_to_python(self.archive_to_upload)
            aux=False
            # apartir de la tercela fila
            row_no=2
            sheet=workbook.sheet_by_index(0)
            data_to_show={}
            employees=self.env['hr.employee'].search([])
            emp_codes=employees.mapped('emp_id')
            attendance_obj=self.env['hr.attendance']
            for i in range(row_no,sheet.nrows):
                line=sheet.row_values(i)
                if line[0] in emp_codes:
                    try:
                        # emp_id
                        emp_id=line[0].strip()
                        emp=employees.filtered(lambda x: x.emp_id==emp_id)
                        # nombre
                        nombre=line[1]
                        # fecha
                        fecha=xlrd.xldate_as_datetime(float(line[4]), workbook.datemode)
                        # estado
                        state=line[8]
                        # entrada
                        entrada_hora=xlrd.xldate_as_datetime(float(line[9])+float(line[4]), workbook.datemode)
                        # salida
                        salida_hora=xlrd.xldate_as_datetime(float(line[10])+float(line[4]), workbook.datemode)

                        # retraso
                        retraso=int(re.sub('\D','',line[12]))
                        # ausente
                        # raise UserError([emp,nombre,state,entrada_hora,salida_hora,retraso])
                        data_to_show[i]=[emp,nombre,state,entrada_hora,salida_hora,retraso]
                    except:
                        pass
            for a in data_to_show.values():
                attendance_obj.create({
                    'employee_id':a[0].id,
                    'check_in':a[3],
                    'check_out':a[4],
                    'delay_hours':a[5]
                })
                aux=True
            if aux:
                return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('¡Éxito!'),
                    'type': 'success',
                    'message': 'Las asistencias fueron creadas con exito',
                    'sticky': False,
                    # 'next': {
                    #     'type': 'ir.actions.client',
                    #     'tag': 'reload'
                    # }
                }
            }
            else:
                return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Nada creado'),
                    'type': 'warning',
                    'message': 'las asistencias estaban vacias, o el formato presenta errores :c',
                    'sticky': False,
                    # 'next': {
                    #     'type': 'ir.actions.client',
                    #     'tag': 'reload'
                    # }
                }
            }




