from email.policy import default
from odoo import models, fields, api
from datetime import date,datetime

class RequestBenefits(models.Model):
    _name ='res.request.benefits'
    _inherit=[ 'mail.thread','mail.activity.mixin' ]

    employee_id=fields.Many2one('hr.employee' ,'Empleado', required=True,tracking=True)
    prestacion=fields.Many2one('hr.prestaciones.employee.line', string="Prestaciones")   
    company_id=fields.Many2one('res.company', default=lambda self: self.env.company)
    date=fields.Date(required=True, string='Fecha de Solicitud', default=date.today(), tracking=True)
    contract_id= fields.Many2one(related='prestacion.contract_id', string="Contrato" )
    antiguedad=fields.Float(string="Antigüedad", tracking=True )
    porcentaje_manual=fields.Boolean(default=False)
    cap_porcentaje=fields.Float(string="Porcentaje", tracking=True)
    disponible=fields.Float(string="Monto Disponible", tracking=True)
    ultima_fecha=fields.Date(string="Fecha del Ultimo de Anticipo", tracking=True)
    motivo_prestacion=fields.Many2one('res.reason.service', string="Motivo de Prestacíon", tracking=True )  
    observacion=fields.Char(string="Observacion") 
    
    @api.onchange('employee_id','cap_porcentaje','porcentaje_manual')
    def _onchange_employee_id(self):

        for rec in self:
            
            rec.prestacion=self.env['hr.prestaciones.employee.line'].search([('parent_id','=',rec.employee_id.id)],limit=1,order="id desc")
            rec.antiguedad = rec.prestacion.prestaciones_acu
            rec.ultima_fecha= rec.prestacion.fecha
            rec.disponible=rec.prestacion.tasa_activa
            
            if rec.prestacion.line_type == 'anticipo':
                rec.ultima_fecha= rec.prestacion.fecha
            else:
                rec.ultima_fecha = False

            if rec.porcentaje_manual:
                
                rec.disponible= (rec.prestacion.prestaciones_acu/100)*rec.cap_porcentaje
            else:

                rec.disponible= rec.prestacion.prestaciones_acu * 0.75
          
    # def report(self):
    #     prestaciones=self.env['hr.prestaciones.employee.line'].search([('parent_id','=',rec.employee_id.id)],limit=1,order="id desc")
    #     for c in prestaciones:

            # if self.tasa_activa !=0:

            # rec.disponible=self.env['hr.prestaciones.employee.line'].search([('tasa_activa','=',rec.disponible)],limit=1,order="id desc")
            # rec.contract_id=self.env['hr.prestaciones.employee.line'].search([('contract_id','=',rec.contract_id.id)],limit=1,order="id desc")

  
       
       
       
       
       
       
       
       
       
       
       
       
       
            # rec.antiguedad=self.env['hr.prestaciones.employee.line'].search([('antiguedad','=', rec.contract_id.id)],limit=1,order="id desc")
            # if rec.antiguedad == 0:
            #     rec.antiguedad=0
      
        
  


















    # date = fields.Datetime('Fecha de solicitud')
    # # employee_id= fields.Many2one('hr.employee', 'Nombre de empleado')
    
    # prestacione= fields.Many2one('hr.prestaciones.employee.line', 'Acumulacion de Prestaciones')
    
    # prestaciones_acu= fields.Float (string="Acumlacion de Prestaciones" , related='prestacione.prestaciones_acu'  )

    # total_disponible= fields.Float(string="Total Disponible", related='prestacione.prestaciones_acu')
    # fecha_ultimo_anti= fields.Date(string="Ultima Fecha de Anticipo", related='prestacione.fecha' )
    # anticipos_otorga= fields.Float(string="Ultimo Anticipo" , related='prestacione.anticipos_otorga')
    
    # def traerdatos(self):
    #     for rec in self:

    #         for empleado in rec.employee_id:

    #             linea_anterior=self.env['hr.prestaciones.employee.line'].search([('parent_id','=',empleado.id)],limit=1,order="id desc")
        
    #     # search(['clean',''],limit=1,order="id desc")