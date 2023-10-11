# -*- coding: utf-8 -*-


from odoo import fields, models,api
from odoo.exceptions import UserError
from datetime import date,datetime
from calendar import monthrange
TODAY = date.today()
class NominaConceptsalarial(models.TransientModel):
    _name = 'res.concept.salarial'
    _description = 'Nomina segun su concepto salarial'

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
    reglas=fields.Many2one('hr.salary.rule',string="Reglas Salariales" )
    employee_id=fields.Many2one('hr.employee',string="Empleado")

    @api.onchange('type_nomina')
    def onchange_type(self):
        for rec in self:
            if rec.type_nomina=="especial":
                rec.filtro='with_payslip_only'
                

    
    def print_report_concept_salarial (self):
        
        # signo=self.env.company.currency_id.symbol
        # domain = [
        #     ('struct_id','=',self.structure.id),
            
        #     ('state','not in',['draft','cancel']),
        #     ('company_id','=',self.env.company.id),
        #     ('date_from','>=',self.fecha_inicio),
        #     ('date_to','<=',self.fecha_final)
        # ]
        # if self.employee_id:
        #     domain += [('employee_id','=',self.employee_id.id)]
        # nominas=self.env['hr.payslip'].search(domain)                          
        # data = []
        # estructura_reglas = self.structure.mapped(lambda r: { "name": r.name, "reglas": r.rule_ids })
       
        

      
        # empleados=nominas.mapped('employee_id.name')
        # lineas = sum(nominas.mapped('line_ids').filtered(lambda x: x.salary_rule_id.id == self.reglas.id).mapped('total'))
        # contlineas = len(nominas.mapped('line_ids').filtered(lambda x: x.salary_rule_id.id == self.reglas.id).mapped('total'))
        # reglas = self.reglas.name
 
        # data={
        #     'form': self.read()[0],
        #     'estructura':self.structure.name,
        #     'company':self.env.company.read()[0],
        #     'logo':self.env.company.logo,
        #     'mes':self.fecha_final.strftime('%B de %Y'),
        #     'inicio':self.fecha_inicio.strftime('%d / %m de %Y'),
        #     'final':self.fecha_final.strftime('%d / %m de %Y'),

        # }

        if self.type_nomina=="normal":
            return self.env.ref('eu_nomina_concepto_salarial.action_report_concepto_salarial').report_action(self)
        else:
            return self.env.ref('eu_nomina_concepto_salarial.action_report_concepto_salarial').report_action(self)
