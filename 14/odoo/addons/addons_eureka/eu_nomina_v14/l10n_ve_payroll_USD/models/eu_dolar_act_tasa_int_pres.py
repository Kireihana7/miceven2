# -*- coding: utf-8 -*-

from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from math import floor
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, timedelta,date
from calendar import monthrange

TODAY=datetime.today()

class HrActTasaIntPresWiz(models.Model):
    
    _inherit="act_tasa_int_pres"


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
                diff_intereses_ref=diff_intereses*prestacion_act.currency_rate_date if prestacion_act.currency_rate_date>1 else prestacion_act.presta_e_inte*prestacion_act.currency_rate_date
                prestacion_act.intereses_ref+=diff_intereses_ref
                prestacion_act.intereses_acum_ref+=diff_intereses_ref
                prestacion_act.presta_e_inte_ref+=diff_intereses_ref
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