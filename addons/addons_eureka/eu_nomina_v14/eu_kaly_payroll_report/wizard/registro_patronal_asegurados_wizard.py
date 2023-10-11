
from odoo import models, fields, api,_
from odoo.exceptions import UserError
class RegistroPatronalAsegurados(models.TransientModel):
    _name = "registro.patronal.asegurados.wizard"

    desde = fields.Date('Desde')
    hasta = fields.Date('Hasta')
    company_id = fields.Many2one('res.company',string='Compañía',required=True,default=lambda self: self.env.company.id,copy=True)
    
    def report_print(self):
        datas = []
        
        employees = self.env['hr.employee'].search([])\
        .filtered(lambda x: x.fecha_inicio and x.fecha_inicio <= self.hasta and (x.fecha_fin and not x.fecha_fin <= self.desde or not x.fecha_fin))


        for employee in employees:
            datas.append({
                'employee': employee.id,
                'name_employee': employee.name,
                'rif_employee': employee.identification_id_2,
                'nationality': employee.nationality,
                'department': employee.department_id.name,
                'birthday_day': employee.birthday.strftime('%d') if employee.birthday else '' ,
                'birthday_mes': employee.birthday.strftime('%m') if employee.birthday else '',
                'birthday_year': employee.birthday.strftime('%Y') if employee.birthday else '',
                'gender': employee.gender,
                'job_title': employee.job_title,

                'street': employee.street if employee.street else '', 
                'parroquia': employee.e_parroquia.name if employee.e_parroquia else '',
                'e_municipio': employee.e_municipio.name if employee.e_municipio else '',
                'city': employee.city_id.name if employee.city_id.name else '',
                'state': employee.state_id.name if employee.state_id.name else '',
                'country': employee.country_id.name if employee.country_id else '',
                'ivss': employee.num_sso if employee.num_sso else '',

                'fecha_inicio_dia': employee.fecha_inicio.strftime('%d'),
                'fecha_inicio_mes': employee.fecha_inicio.strftime('%m'),
                'fecha_inicio_year': employee.fecha_inicio.strftime('%Y'),

                'fecha_fin_dia': employee.fecha_fin.strftime('%d') if employee.fecha_fin else '' ,
                'fecha_fin_mes': employee.fecha_fin.strftime('%m') if employee.fecha_fin else '' ,
                'fecha_fin_year': employee.fecha_fin.strftime('%Y') if employee.fecha_fin else '' ,
                'sal_diario': "{0:.2f}".format(float(employee.contract_id.wage) / 30),
                'sal_semanal': "{0:.2f}".format((float(employee.contract_id.wage) / 30) * 7),
                'sal_mensual': "{0:.2f}".format(float(employee.contract_id.wage)),

                'ivss_semanal_empleado': "{0:.2f}".format(float((float(employee.contract_id.wage * 12) / 52 ) * (4 / 100))),
                'ivss_semanal_empleador': "{0:.2f}".format(float((float(employee.contract_id.wage * 12) / 52 ) * (float(employee.company_id.por_riesgo) / 100)) if employee.company_id.por_riesgo else ''),
                'total_aporte_ivss': "{0:.2f}".format(float(((employee.contract_id.wage * 12) / 52 ) * (4 / 100)) + float(((float(employee.contract_id.wage) * 12) / 52 ) * (float(employee.company_id.por_riesgo) / 100))),

                'rpe_semanal_empleado': "{0:.2f}".format(((float(employee.contract_id.wage) * 12) / 52 ) * (float(employee.company_id.por_empleado_rpe) / 100)),
                'rpe_semanal_empleador': "{0:.2f}".format(((float(employee.contract_id.wage) * 12) / 52 ) * (float(employee.company_id.por_empresa_rpe ) / 100) if employee.company_id.por_empresa_rpe else ''),
                'total_aprte_rpe': "{0:.2f}".format(((float(employee.contract_id.wage) * 12) / 52 ) * (float(employee.company_id.por_empleado_rpe) / 100) + ((float(employee.contract_id.wage) * 12) / 52 ) * (float(employee.company_id.por_empresa_rpe ) / 100))
                
            })

        res = {
            'fecha_desd_dia': self.desde.strftime('%d'),
            'fecha_desd_mes': self.desde.strftime('%m'),
            'fecha_desd_year': self.desde.strftime('%Y'),
            'fecha_hasta_dia': self.hasta.strftime('%d'),
            'fecha_hasta_mes': self.hasta.strftime('%m'),
            'fecha_hasta_year': self.hasta.strftime('%Y'),
            'company_id': self.company_id,
            'docs': datas,
        }

        data = {'form': res}
        return self.env.ref('eu_kaly_payroll_report.custom_action_report_patronal_asegurados').report_action(self, data=data)