# -*- coding: utf-8 -*-


from unicodedata import category
from odoo import fields, models,api
from odoo.exceptions import UserError
from datetime import date,datetime
from calendar import monthrange
TODAY = date.today()
class NominaGlobalWizard(models.TransientModel):
    _name = 'nomina.global.wizard'
    _description = 'Nómina Global'

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
    @api.onchange('type_nomina')
    def onchange_type(self):
        for rec in self:
            if rec.type_nomina=="especial":
                rec.filtro='with_payslip_only'
                

    def print_report(self):
        departamento=self.env['hr.department'].sudo().search_read([('company_id','=',self.env.company.id)])
        empleados=self.env['hr.employee'].sudo().search([('company_id','=',self.env.company.id)])
        signo=self.currency_id.symbol
        nominas=self.env['hr.payslip'].sudo().search([('struct_id','=',self.structure.id),('type_struct_category','=',self.type_nomina),('state','not in',['draft','cancel']),('company_id','=',self.env.company.id),('date_from','>=',self.fecha_inicio),('date_to','<=',self.fecha_final)])
        
        linea_nomina=[]
        for empleado in empleados:
            nominas_empleado=False
            contrato=empleado.contract_id

            if self.type_nomina=="normal":
                #pasamos al siguiente empleado si no cumple con los filtros
                if self.filtro in ["with_contracts","with_payslip_only"] and not contrato:
                    continue
                nominas_empleado=nominas.filtered(lambda x:x.employee_id==empleado)
                if self.filtro=="with_payslip_only" and not nominas_empleado:
                    continue
                linea={}
                #se asigna como un dict
                linea['employee']=empleado.name
                linea['ci']=empleado.identification_id_2
                linea['department']=empleado.department_id.id
                if not contrato:
                    linea["error"]="ESTE EMPLEADO NO POSEE CONTRATO"
                elif not nominas_empleado:
                    linea['date_start']=contrato.date_start
                    linea["error"]="ESTE EMPLEADO NO POSEE NOMINAS PARA ESTA FECHA"
                else:
                    linea['date_start']=contrato.date_start
                    linea['position']=contrato.job_id.name
                    linea['sal_mensual']=contrato.wage
                    linea['sal_diario']=round(contrato.wage/30,2)
                    #se busca la sumatiria de los dias trabajados y descansados en cada nomina

                    linea['worked_days']=sum((sum(x.worked_days_line_ids.filtered(lambda f: f.work_entry_type_id.is_leave==False).mapped("number_of_days")) for x in nominas_empleado))
                    linea['free_days']=sum((sum(x.worked_days_line_ids.filtered(lambda f: f.work_entry_type_id.is_leave==True).mapped("number_of_days")) for x in nominas_empleado))
                    #se calculan las asignaciones por dias y total
                    linea['payed_worked_days']=sum(x.line_ids.filtered(lambda f: f.code=='SU').total for x in nominas_empleado)
                    linea['payed_free_days']=sum(x.line_ids.filtered(lambda f: f.code=='DDES').total for x in nominas_empleado)
                    linea['total_asignaciones']=round(linea['payed_worked_days']+linea['payed_free_days'],2)

                    #las retenciones deducciones y demas
                    linea['s.s.o.']= sum(x.line_ids.filtered(lambda f: f.code=='S.S.O').total for x in nominas_empleado)
                    linea['s.s.o.empleador']= sum(x.line_ids.filtered(lambda f: f.code=='SSO-EMPRESA').total for x in nominas_empleado)
                    linea['r.p.e.']= sum(x.line_ids.filtered(lambda f: f.code=='R.P.E').total for x in nominas_empleado)
                    linea['r.p.e.empleador']= sum(x.line_ids.filtered(lambda f: f.code=='RPE-EMPRESA').total for x in nominas_empleado)
                    linea['faov']= sum(x.line_ids.filtered(lambda f: f.code=='F.A.O.V.').total for x in nominas_empleado)
                    linea['faov.empleador']= sum(x.line_ids.filtered(lambda f: f.code=='F.A.O.V.-EMPRESA').total for x in nominas_empleado)
                    # linea['inces']= sum(x.line_ids.filtered(lambda f: f.code=='INCES').amount for x in nominas_empleado)
                    # linea['inces.patronal']= sum(x.line_ids.filtered(lambda f: f.code=='INCES-EMPRESA').amount for x in nominas_empleado)
                    
                    linea['ausencias']=(self.fecha_final-self.fecha_inicio).days+1-(linea['worked_days']+ sum(x.domingo_periodo + x.sabado_periodo for x in nominas_empleado))
                    # linea['islr']=sum(x.line_ids.filtered(lambda f: f.code=='ISLR').amount for x in nominas_empleado)
                    # +linea['inces']+linea['islr']
                    linea['total_deducciones']=round(linea['s.s.o.']+linea['r.p.e.']+linea['faov'],2)
                    linea['total']=round(linea['total_asignaciones']-linea['total_deducciones'],2)
                
            else:
                if self.filtro in ["with_contracts","with_payslip_only"] and not contrato:
                    continue
                nominas_empleado=nominas.filtered(lambda x:x.employee_id==empleado)
                if self.filtro=="with_payslip_only" and not nominas_empleado:
                    continue
                contrato=False
                contrato=empleado.contract_id
                linea={}
                #se asigna como un dict
                linea['employee']=empleado.name
                linea['ci']=empleado.identification_id_2
                linea['department']=empleado.department_id.id
                linea['date_start']=contrato.date_start
                linea['position']=contrato.job_id.name
                linea['sal_mensual']=contrato.wage
                linea['sal_diario']=round(contrato.wage/30,2)
                #se busca la sumatiria de los dias trabajados y descansados en cada nomina
                linea['sal_complemento']=contrato.complemento
            
            linea_nomina.append(linea)
        deptset=set([x['department'] for x in linea_nomina])
        departamento_filtrado= list(filter(lambda dept: dept['id'] in deptset,departamento))
        if not departamento_filtrado:
            raise UserError("No hay entradas para mostrar!")
        data={
            'ids': self.ids,
            'model': self._name,
            'form': self.read()[0],
            'departamentos':departamento_filtrado,
            'lineas':linea_nomina,
            'company':self.env.company.read()[0],
            'logo':self.env.company.logo,
            'mes':self.fecha_final.strftime('%B de %Y'),
            'inicio':self.fecha_inicio.strftime('%d / %m de %Y'),
            'final':self.fecha_final.strftime('%d / %m de %Y'),
            'symbol':signo

        }
        if self.type_nomina=="normal":
            return self.env.ref('l10n_ve_payroll.action_report_global_nomina').report_action(self,data=data)
        else:
            return self.env.ref('l10n_ve_payroll.action_report_sal_comple_nomina').report_action(self,data=data)

    def print_report2(self):
        departamento=self.env['hr.department'].sudo().search_read([('company_id','=',self.env.company.id)])
        empleados=self.env['hr.employee'].sudo().search([('company_id','=',self.env.company.id)])
        signo=self.currency_id.symbol
        nominas=self.env['hr.payslip'].sudo().search([('struct_id','=',self.structure.id),('type_struct_category','=',self.type_nomina),('state','not in',['draft','cancel']),('company_id','=',self.env.company.id),('date_from','>=',self.fecha_inicio),('date_to','<=',self.fecha_final)])
        
        linea_nomina=[]
        suma=0
        for empleado in empleados:
            nominas_empleado=False
            contrato=False
            contrato=empleado.contract_id

            
                #pasamos al siguiente empleado si no cumple con los filtros
            if self.filtro in ["with_contracts","with_payslip_only"] and not contrato:
                    continue
            nominas_empleado=nominas.filtered(lambda x:x.employee_id==empleado)
            if self.filtro=="with_payslip_only" and not nominas_empleado:
                    continue
            linea={}
                #se asigna como un dict
            linea['employee']=empleado.name
            linea['ci']=empleado.identification_id_2
            linea['department']=empleado.department_id.id
            linea['eid']=empleado.id
            linea['cuentabanco']=empleado.account_number_2
            if not contrato:
                    linea["error"]="ESTE EMPLEADO NO POSEE CONTRATO"
            elif not nominas_empleado:
                    linea['date_start']=contrato.date_start
                    linea["error"]="ESTE EMPLEADO NO POSEE NOMINAS PARA ESTA FECHA"
            else:
                    linea['date_start']=contrato.date_start
                    linea['position']=contrato.job_id.name
                    linea['sal_mensual']=contrato.wage
                    linea['sal_diario']=round(contrato.wage/30,2)
                    #se busca la sumatiria de los dias trabajados y descansados en cada nomina

                    linea['total']=sum(x.total_sum for x in nominas_empleado)
                    suma+=linea['total']
                    
                        #se busca la sumatiria de los dias trabajados y descansados en cada nomina
                    linea['sal_complemento']=contrato.complemento
            
            linea_nomina.append(linea)
        deptset=set([x['department'] for x in linea_nomina])
        departamento_filtrado= list(filter(lambda dept: dept['id'] in deptset,departamento))
        if not departamento_filtrado:
            raise UserError("No hay entradas para mostrar!")
        data={
            'ids': self.ids,
            'model': self._name,
            'form': self.read()[0],
            'departamentos':departamento_filtrado,
            'estructura':self.structure.name,
            'hoy':TODAY,
            'hora':datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()),"%H:%M:%S"),
            'lineas':linea_nomina,
            'company':self.env.company.read()[0],
            'logo':self.env.company.logo,
            'mes':self.fecha_final.strftime('%B de %Y'),
            'inicio':self.fecha_inicio.strftime('%d / %m de %Y'),
            'final':self.fecha_final.strftime('%d / %m de %Y'),
            'symbol':signo,
            'totaltotal':suma
        }
        
        return self.env.ref('l10n_ve_payroll.action_report_global_pago_CSV').report_action(self,data=data)
        
    def print_report3(self):
        empleado=self.env['hr.employee']

        departamento=self.env['hr.department'].sudo().search_read([('company_id','=',self.env.company.id)])
        empleados=self.env['hr.employee'].sudo().search([('company_id','=',self.env.company.id)])
        signo=self.currency_id.symbol
        nominas=self.env['hr.payslip'].sudo().search([('struct_id','=',self.structure.id),('type_struct_category','=',self.type_nomina),('state','not in',['draft','cancel']),('company_id','=',self.env.company.id),('date_from','>=',self.fecha_inicio),('date_to','<=',self.fecha_final)])
        
        linea_nomina=[]
        suma=0
        
        
        data={
            'doc_ids':empleados.filtered(lambda x: x.contract_id.is_variable_wage==True).mapped('id'),
            'doc_model': 'hr.employee',
            'estructura':self.structure.name,
            'inicio':self.fecha_inicio,
            # strftime('%d / %m de %Y')
            'final':self.fecha_final,
            # .strftime('%d / %m de %Y')
            'hoy':TODAY,
            'hora':datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()),"%H:%M:%S"),
        }
       
            # 'departamentos':departamento_filtrado,
            # 'company':self.env.company.read()[0],
            # 'logo':self.env.company.logo,
            # 'mes':self.fecha_final.strftime('%B de %Y'),
            # 'symbol':signo,
            # 'totaltotal':suma
        
        return self.env.ref('l10n_ve_payroll.action_report_acum_nom_varia_CSV').report_action(empleados,data=data)

    def print_report4 (self):
    
        departamento=self.env['hr.department'].sudo().search_read([('company_id','=',self.env.company.id)])
        empleados=self.env['hr.employee'].sudo().search([('company_id','=',self.env.company.id)])
        signo=self.currency_id.symbol
        nominas=self.env['hr.payslip'].sudo().search([
            ('struct_id','=',self.structure.id),
            ('type_struct_category','=',self.type_nomina),
            ('state','not in',['draft','cancel']),
            ('company_id','=',self.env.company.id),
            ('date_from','>=',self.fecha_inicio),
            ('date_to','<=',self.fecha_final),
             
        ])                          

      
                         
  
        linea_nomina=[]
        for empleado in empleados:
            nominas_empleado=False
            contrato=empleado.contract_id
            
            if not contrato:
                contrato = self.env['hr.contract'].search([('employee_id','=',empleado.id),('state','=','open')],limit=1) or False
            reglas={}
            if self.type_nomina=="normal":
                #pasamos al siguiente empleado si no cumple con los filtros
                if self.filtro in ["with_contracts","with_payslip_only"] and not contrato:
                    continue
                nominas_empleado=nominas.filtered(lambda x:x.employee_id==empleado)
                if self.filtro=="with_payslip_only" and not nominas_empleado:
                    continue
  
                linea={}
                #se asigna como un dict
                linea['employee']=empleado.name
                linea['ci']=empleado.identification_id_2
                linea['department']=empleado.department_id.id
                linea['position']=empleado.job_title
                linea['emp_id']=empleado.emp_id

                if not contrato:
                    linea["error"]="ESTE EMPLEADO NO POSEE CONTRATO"
                elif not nominas_empleado:
                    linea['date_start']=contrato.date_start
                    linea["error"]="ESTE EMPLEADO NO POSEE NOMINAS PARA ESTA FECHA"
                else:
                    linea['date_start']=contrato.date_start
                    linea['position']=contrato.job_id.name
                    linea['sal_mensual']=contrato.wage
                    linea['sal_diario']=round(contrato.wage/30,2)
                    #se busca la sumatiria de los dias trabajados y descansados en cada nomina
                    
                    regla_nomina= (nominas_empleado.mapped('line_ids'))
                    
                    

                    for rule in regla_nomina:
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
                            
                    # egreso={}
                    # for egreso in linea['rules'].values():
                    #     egreso[0]
                    #     breakpoint()
                    # egreso={}

                    # for depura in linea['rules'].values():
                    #     if  egreso.get|[rule.code,True]:
                           


                 
            else:
                if self.filtro in ["with_contracts","with_payslip_only"] and not contrato:
                    continue
                nominas_empleado=nominas.filtered(lambda x:x.employee_id==empleado)
                if self.filtro=="with_payslip_only" and not nominas_empleado:
                    continue
                contrato=False
                contrato=empleado.contract_id
                linea={}
                #se asigna como un dict
                linea['employee']=empleado.name
                linea['ci']=empleado.identification_id_2
                linea['department']=empleado.department_id.id
                linea['date_start']=contrato.date_start
                linea['position']=contrato.job_id.name
                linea['sal_mensual']=contrato.wage
                linea['sal_diario']=round(contrato.wage/30,2)
                #se busca la sumatiria de los dias trabajados y descansados en cada nomina
                linea['sal_complemento']=contrato.complemento
            linea['rules']=reglas
            
            linea_nomina.append(linea)
        deptset=set([x['department'] for x in linea_nomina])
        departamento_filtrado= list(filter(lambda dept: dept['id'] in deptset,departamento))
        if not departamento_filtrado:
            raise UserError("No hay entradas para mostrar!")
        data={
            'ids': self.ids,
            'model': self._name,
            'form': self.read()[0],
            'departamentos':departamento_filtrado,
            'estructura':self.structure.name,
            'lineas':linea_nomina,
            'company':self.env.company.read()[0],
            'logo':self.env.company.logo,
            'mes':self.fecha_final.strftime('%B de %Y'),
            'inicio':self.fecha_inicio.strftime('%d / %m de %Y'),
            'final':self.fecha_final.strftime('%d / %m de %Y'),
            'symbol':signo
            

        }
        # for pagos in nominas:
        #     for line in pagos.line_ids:                    
        #         if reglas[line.name]:
        #             reglas[line.name] += reglas[line]
        #         else:
        #             reglas[line.name]=[category]
        # entrada={empleado:empleados, reglas:reglas}


        # listado.append(entrada)
    
        # reglas={

        # }
        # for lineas de reglas:
        #     if reglas[lineas]:
        #         reglas[lineas]+=monot
        #     else:
        #         regla[lineas]=monto
        if self.type_nomina=="normal":
            return self.env.ref('l10n_ve_payroll.action_report_pago_global_cscv_new').report_action(self,data=data)
        else:
            return self.env.ref('l10n_ve_payroll.action_report_pago_global_cscv_new').report_action(self,data=data)
    
class ParticularReport(models.AbstractModel):
    _name = 'report.l10n_ve_payroll.report_acum_rel_nomina_var'

    def _get_report_values(self, docids, data=None):
        # get the report action back as we will need its data
        
        # return a custom rendering context
        return {
            'doc_ids':data.get("doc_ids"),
            'doc_model': data.get("doc_model"),
            'docs':self.env['hr.employee'].search([('id','in',data.get("doc_ids"))]),
            'datas':data

        }