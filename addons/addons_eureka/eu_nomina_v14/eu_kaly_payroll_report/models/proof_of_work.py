# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class ProofOfWorkWizard(models.Model):
    _inherit = 'hr.employee'

    def print_report(self) :
        datas = []
        datos = []
        line_data = []
        employee_ids = self.env['hr.employee'].browse(self._context['active_ids'])

        for employee in employee_ids:
            nomina = self.env['hr.payslip'].search([('is_anihilation','=',False),('is_utility','=',False),
                    ('employee_id','=',employee.id),('type_struct_category','in',['normal','especial'])])
                    
            nomina_line = self.env['hr.payslip'].search([('is_anihilation','=',False),('is_utility','=',False),
                    ('employee_id','=',employee.id),('type_struct_category','in',['normal','especial'])]) \
                    .mapped('line_ids').filtered(lambda x: x.category_id.code=='BASIC').mapped('total')
            
            for nom in nomina:
                datos.append({
                    'fecha': nom.date_from.strftime('%Y'),
                    'total': sum(nomina_line),
                })

            # for nomline in nomina_line:
            # line_data.append({
            #     'total': nomina_line,
            # })

            datas.append({
                'employee_id': employee.id,
                'name_employee': employee.name,
                'rif_employee': employee.identification_id_2,
                'nationality': employee.nationality,
                'department': employee.department_id.name,
                # 'year_start': employee.fecha_inicio.strftime('%Y')  if employee.fecha_inicio else '',
                # 'year_end': employee.fecha_fin.strftime('%Y') if employee.fecha_fin else '',
                
                'fecha_inicio_dia': employee.fecha_inicio.strftime('%d') if employee.fecha_inicio else '00',
                'fecha_inicio_mes': employee.fecha_inicio.strftime('%m') if employee.fecha_inicio else '00',
                'fecha_inicio_year': employee.fecha_inicio.strftime('%Y') if employee.fecha_inicio else '0000',
                'fecha_fin_dia': employee.fecha_fin.strftime('%d') if employee.fecha_fin else '00',
                'fecha_fin_mes': employee.fecha_fin.strftime('%m') if employee.fecha_fin else '00',
                'fecha_fin_year': employee.fecha_fin.strftime('%Y') if employee.fecha_fin else '0000',
                'sueldo': employee.contract_id.wage,
                'letter_rif': self.env.company.rif.upper()[:1],
                # "nomina": nomina,
                # "nomina_line": nomina_line,
                
            })
        
        # breakpoint()

        res = {
            'documents': datas,
            'datos': datos,
            'line_data': line_data
        }

        data = {
            'form': res
        }

        return self.env.ref('eu_kaly_payroll_report.custom_action_report_proof_work').report_action(self,data=data)

