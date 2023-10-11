from datetime import datetime, date

from odoo import fields, models
import locale
MONTH_LIST={
'01':'Enero',
'02':'Febrero',
'03':'Marzo',
'04':'Abril',
'05':'Mayo',
'06':'Junio',
'07':'Julio',
'08':'Agosto',
'09':'Septiembre',
'10':'Octubre',
'11':'Noviembre',
'12':'Diciembre'}

class ConstanciaTrabajo(models.TransientModel):
    _name = 'hr.constancia.trabajo.wizard'
    _description = 'Constancia de trabajo'

    to_who = fields.Text('A quien se va dirigir?')
    fecha_expedition = fields.Date('Fecha expedición', default=date.today())
    company_id = fields.Many2one('res.company',string='Compañía',required=True,default=lambda self: self.env.company.id,copy=True,readonly=1)


    def print_report(self):
        datas = []
        
        employee_ids = self.env['hr.employee'].browse(self._context['active_ids'])
        # locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
        
        for employee in employee_ids:
            # coordinador de rrHH
            job_title = self.company_id.boss_rrhh.job_title
            name_jefe_rrHH = self.company_id.boss_rrhh.name
            rif_jefe_rrHH = self.company_id.boss_rrhh.identification_id_2
            datas.append({
                'name_employee': employee.name,
                'rif_employee': employee.identification_id_2,
                'department': employee.department_id.name,
                'fecha_inicio': employee.fecha_inicio.strftime('%d/%m/%Y'),
                'sueldo': employee.contract_id.wage,
                'cesta_ticket': employee.contract_id.cesta_ticket,
                'job_title_employee': employee.job_title,
                'job_title': job_title,
                'name_jefe_rrHH': name_jefe_rrHH,
                'rif_jefe_rrHH': rif_jefe_rrHH,
                'to_who': self.to_who,
                'company_id': self.company_id,
                'dia_expedition': self.fecha_expedition.strftime('%d'),
                'mes_expedition': MONTH_LIST[self.fecha_expedition.strftime('%m')],
            })

        res = {
            'documents': datas,
        }

        data = {
            'form': res,
        }
        
        return self.env.ref('l10n_ve_payroll.custom_action_report_constancia_trabajo').report_action([],data=data)

