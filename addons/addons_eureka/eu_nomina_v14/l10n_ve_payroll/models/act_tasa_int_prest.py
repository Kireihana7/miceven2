from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
from xlrd import open_workbook
import base64

TODAY = date.today()
class HrActTasaIntPresWiz(models.Model):
    
    _name="act_tasa_int_pres"
    _inherit=['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company',string="Compañía", default=lambda self: self.env.company.id,tracking=True,invisible=True)

    fecha = fields.Date("fecha")
    tasa = fields.Float('Tasa Activa')
    promedio = fields.Float('Tasa Promedio')


    def act_tasa_act(self):
        prestaciones=self.env['hr.prestaciones.employee.line'].search([('company_id','=',self.company_id.id)])
        line=[]
           
        for rec in self.sorted('fecha'):
            if not rec.env.company.journal_for_prestaciones:
                raise UserError("No existe diario para prestaciones en la compañia, por favor ingresar uno en configuración de prestaciones")
            
            prestaciones_actualizar=prestaciones.filtered(lambda x: x.fecha.strftime("%m/%Y") == rec.fecha.strftime("%m/%Y") and x.line_type=="prestacion")
            for prestacion_act in prestaciones_actualizar:
                line=[]
                
                prestacion_act.tasa_activa=rec.tasa
                previo_valor_interes=prestacion_act.intereses
                intereses=(prestacion_act.prestaciones_acu*prestacion_act.tasa_activa)/(100*12) #intereses obtenido
                diff_intereses=intereses-previo_valor_interes
                prestacion_act.intereses=intereses
                prestacion_act.intereses_acum+=diff_intereses
                prestacion_act.presta_e_inte+=diff_intereses
                chunk_prestaciones=prestaciones.filtered(lambda x: x.parent_id==prestacion_act.parent_id and x.fecha>prestacion_act.fecha and x.line_type!="clean")
                for p in chunk_prestaciones:
                    # me parece que si le pagan de mas no le va a devolver el dinero asi que aja
                    if p.intereses_acum+diff_intereses>=0:
                        p.intereses_acum+=diff_intereses
                    if p.presta_e_inte+diff_intereses>=0:
                        p.presta_e_inte+=diff_intereses

                
                if abs(diff_intereses)>0:
                    apunte=rec.env['account.move'].sudo().create({
                    'date':rec.fecha,
                    'journal_id':rec.env.company.journal_for_prestaciones.id
                    })
                    if diff_intereses>0:
                        line.append({
                            'account_id':rec.env.company.asiento_interes_pres.id,
                            'name': f"intereses {rec.fecha} - {prestacion_act.parent_id.name}",
                            'debit':abs(diff_intereses),
                            'move_id':apunte.id
                        })
                        line.append({
                            'account_id':rec.env.company.asiento_interes_paga.id,
                            'name': f"intereses {rec.fecha} - {prestacion_act.parent_id.name}",
                            'credit':abs(diff_intereses),
                            'move_id':apunte.id
                        })
                    else:
                        line.append({
                            'account_id':rec.env.company.asiento_interes_pres.id,
                            'name': f"intereses {rec.fecha} - {prestacion_act.parent_id.name}",
                            'credit':abs(diff_intereses),
                            'move_id':apunte.id
                        })
                        line.append({
                            'account_id':rec.env.company.asiento_interes_paga.id,
                            'name': f"intereses {rec.fecha} - {prestacion_act.parent_id.name}",
                            'debit':abs(diff_intereses),
                            'move_id':apunte.id
                        })
                    for li in line:
                        apunte.line_ids+=rec.env['account.move.line'].create(li)
            employees=prestaciones_actualizar.mapped('parent_id')
            message=f"Se actualizo la tasa de prestaciones a una tasa de {rec.tasa} en las lineas de prestaciones de los empleados {','.join([e.name for e in employees])} con fecha {rec.fecha.strftime('%m / %Y')}"
            rec.message_post(body=message,subject='Estatus de uso')
    # def readed(self):

    #     # LEEEMOS EL ARCHIVOOOOOOO
    #     file_data = base64.b64decode(self.archivo)
    #     wb = open_workbook(file_contents=file_data)
    #     page=wb.sheet_by_index(0)
    #     # nos paramos en el punto inicial
    #     data_storm=[]
    #     auxiliar_year=1
    #     data_line=[]
    #     for i in range(0,page.nrows-8-3):
    #         # obtenemos el año por el cual transitamos
    #         if str(page.cell_value(i+8,0)).isdigit() and int(page.cell_value(i+8,0))!=auxiliar_year:
    #             auxiliar_year=int(page.cell_value(i+8,0))
    #             data_storm.append(data_line)
    #             data_line=[]
    #         elif not str(page.cell_value(i+8,0)).isdigit() and page.cell_value(i+8,0)!=False:
    #             data_line.append([auxiliar_year,page.cell_value(i+8,0),page.cell_value(i+8,5)])

        # raise UserError(data_storm)



