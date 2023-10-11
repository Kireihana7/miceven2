# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date,datetime
from odoo.exceptions import UserError


class ProofOfWorkEmployee(models.Model):
    _inherit = 'hr.employee'

    def print_report(self) :
        datas = []
        
        for employee in self:
            if not self.fecha_inicio:
                raise UserError('El empleado Deber tener una fecha de ingreso...!')
    
            set_years = range(int(employee.fecha_inicio.strftime('%Y')) , date.today().year + 1)

            months = [
                ('01','ENERO'),('02','FEBRERO'),('03','MARZO'),('04','ABRIL'),('05','MAYO'),('06','JUNIO'),('07', 'JULIO'),('08', 'AGOSTO'),
                ('09', 'SEPTIEMBRE'),('10','OCTUBRE'),('11','NOVIEMBRE'),('12','DICIEMBRE')
            ]

            datas.append({
                'employee_id': employee.id,
                'name_employee': employee.name,
                'rif_employee': employee.identification_id_2,
                'nationality': employee.nationality,
                'department': employee.department_id.name,
                
                'fecha_inicio_dia': employee.fecha_inicio.strftime('%d') if employee.fecha_inicio else '00',
                'fecha_inicio_mes': employee.fecha_inicio.strftime('%m') if employee.fecha_inicio else '00',
                'fecha_inicio_year': employee.fecha_inicio.strftime('%Y') if employee.fecha_inicio else '0000',

                'fecha_fin_dia': employee.fecha_fin.strftime('%d') if employee.fecha_fin else '00',
                'fecha_fin_mes': employee.fecha_fin.strftime('%m') if employee.fecha_fin else '00',
                'fecha_fin_year': employee.fecha_fin.strftime('%Y') if employee.fecha_fin else '0000',

                'sueldo': employee.contract_id.wage,
                'letter_rif': self.env.company.rif.upper()[:1],
                'years': list(set_years)[-6:],
                'months': months
            })
                

        res = {
            'documents': datas,
        }

        data = {
            'form': res
        }

        return self.env.ref('eu_kaly_payroll_report.custom_action_report_proof_work').report_action(self,data=data)

