
from odoo import fields, models,api
from odoo.exceptions import UserError
from datetime import date,datetime
from calendar import monthrange
TODAY = date.today()

class PayrollBranchReport(models.TransientModel):
    _name = "payroll.branch.report.wizard"
    _description = "payroll_branch_report_wizard"

    @api.model
    def _default_fecha_inicio(self):
        
        if TODAY.day <=15:
            current_date = date(TODAY.year,TODAY.month,1)
        else:
            current_date = date(TODAY.year,TODAY.month,16)
        return current_date
    @api.model
    def _default_fecha_final(self):
        
        if TODAY.day <=15:
            last_date = date(TODAY.year,TODAY.month,15)
        else:
            last_date = date(TODAY.year,TODAY.month,monthrange(TODAY.year, TODAY.month)[1])
        return last_date

    fecha_inicio = fields.Date("Fecha Inicio", default=_default_fecha_inicio)
    fecha_final = fields.Date("Fecha Final", default=_default_fecha_final)
    type_nomina=fields.Selection([('normal', 'Normal'),
        ('especial', 'Especial'),
        ('vacation', 'Vacaciones'),('advance','Adelanto'),
        ('utilities','Utilidades')
    ],  default="normal", string="Tipo Nómina")
    structure=fields.Many2one('hr.payroll.structure', string="Estructura especial")
    filtro=fields.Selection([('all', 'Sin filtrado'),
        ('with_contracts', 'Contratados'),
        ('with_payslip_only', 'Con nómina pagada'),
    ],  default="with_contracts", string="Filtrar por")
    currency_id = fields.Many2one("res.currency", string="Moneda",default=lambda self: self.env.company.currency_id)
    branch_id = fields.Many2one('res.branch',string="Sucursal")
    company_id = fields.Many2one('res.company',string='Compañía',required=True,default=lambda self: self.env.company.id,copy=True,readonly=1)
    @api.onchange('type_nomina')
    def onchange_type(self):
        for rec in self:
            if rec.type_nomina=="especial":
                rec.filtro='with_payslip_only'

    def print_report(self):
        empleados=self.env['hr.employee'].sudo().search([('company_id','=',self.env.company.id),('branch_id','=',self.branch_id.id)])
        if not empleados:
            raise UserError("No hay empleado con nomina en estas fechas!")
        signo=self.currency_id.symbol
        nominas=self.env['hr.payslip'].search([
            ('struct_id','=',self.structure.id),
            ('type_struct_category','=',self.type_nomina),
            ('state','not in',['draft','cancel']),
            ('company_id','=',self.env.company.id),
            ('date_from','>=',self.fecha_inicio),
            ('date_to','<=',self.fecha_final),
        ])    

        if not nominas:
            raise UserError('No hay nominas para en este periodo..!')                      

        linea_nomina=[]
        for empleado in empleados:
            nominas_empleado=False
            lineas_nomina = False
            contrato=False
            contrato=empleado.contract_id
            
            if not contrato:
                contrato = self.env['hr.contract'].search([('employee_id','=',empleado.id),('state','=','open')],limit=1) or False
            if self.type_nomina=="normal":
                nominas_empleado=nominas.filtered(lambda x:x.employee_id==empleado)
                lineas_nomina = nominas_empleado.mapped('line_ids')

                if self.filtro in ["with_contracts","with_payslip_only"] and not contrato:
                    continue
                if self.filtro=="with_payslip_only" and not nominas_empleado:
                    continue
                
                reglas = {}
                if not lineas_nomina:
                    continue
                    # raise UserError("ESTE EMPLEADO NO POSEE NOMINAS PARA ESTA FECHA")
                    # raise UserError(nominas_empleado)
                
                for rule in lineas_nomina:
                    if rule.salary_rule_id.appears_on_payslip_receipt:
                        if reglas.get(rule.code,False):
                            reglas[rule.code][3]+=rule.quantity
                            reglas[rule.code][4]+=rule.total
                        else:
                            reglas[rule.code]=[
                                rule.code,
                                rule.category_id.code,
                                rule.salary_rule_id, 
                                rule.quantity,
                                rule.total,
                                rule.name,
                            ]
  
                linea={
                    'employee': empleado.name,
                    'ci':empleado.identification_id_2,
                    'department':empleado.department_id.name,
                    'job_title': empleado.job_title,
                    'emp_id': empleado.emp_id,
                    #reglas
                    'rules': reglas,

                    'date_start': contrato.date_start,
                    'job_name': contrato.job_id.name,
                    'sal_mensual': contrato.wage,
                    'sal_diario': round(contrato.wage/30,2),
                }
   
            else:
                # contrato=False
                # contrato=empleado.contract_id
                nominas_empleado=nominas.filtered(lambda x:x.employee_id==empleado)
                lineas_nomina = nominas_empleado.mapped('line_ids')

                if self.filtro in ["with_contracts","with_payslip_only"] and not contrato:
                    continue

                if self.filtro=="with_payslip_only" and not nominas_empleado:
                    continue
                
                reglas={}

                if not lineas_nomina:
                    continue
                    # raise UserError("ESTE EMPLEADO NO POSEE NOMINAS PARA ESTA FECHA")
                    # raise UserError(nominas_empleado)
                
                for rule in lineas_nomina:
                    if rule.salary_rule_id.appears_on_payslip_receipt:
                        if reglas.get(rule.code,False):
                            reglas[rule.code][3]+=rule.quantity
                            reglas[rule.code][4]+=rule.total
                        else:
                            reglas[rule.code]=[
                                rule.code,
                                rule.category_id.code,
                                rule.salary_rule_id, 
                                rule.quantity,
                                rule.total,
                                rule.name,
                            ]

                linea={
                    'employee': empleado.name,
                    'ci':empleado.identification_id_2,
                    'department':empleado.department_id.name,
                    'job_title': empleado.job_title,
                    'emp_id': empleado.emp_id,
                    
                    'rules': reglas,

                    'date_start': contrato.date_start,
                    'job_name': contrato.job_id.name,
                    'sal_mensual': contrato.wage,
                    'sal_diario': round(contrato.wage/30,2),
                    'sal_complemento': contrato.complemento
                }
            
            linea_nomina.append(linea)
         
        
        res={
            'ids': self.ids,
            'model': self._name,
            'form': self.read()[0],
            'estructura':self.structure.name,
            'lineas':linea_nomina,
            'company':self.env.company.read()[0],
            'logo':self.env.company.logo,
            'mes':self.fecha_final.strftime('%B de %Y'),
            'inicio':self.fecha_inicio.strftime('%d / %m de %Y'),
            'final':self.fecha_final.strftime('%d / %m de %Y'),
            'symbol':signo,
            'sucursal': self.branch_id.name,
            'type_nomina': self.type_nomina,
            'company_id': self.company_id,
        }

        # breakpoint()

        data = {
            'form': res
        }

        if self.type_nomina=="normal":
            return self.env.ref('eu_payroll_branch_report.custom_action_report_payroll_branch').report_action(self,data=data)
        else:
            return self.env.ref('eu_payroll_branch_report.custom_action_report_payroll_branch').report_action(self,data=data)