import datetime
from datetime import date
from datetime import timedelta
from odoo.exceptions import UserError
from odoo import models, fields, api


class AccountMoveHeredit(models.Model):
    _inherit = 'account.move'

    sale_id= fields.Many2one ("sale.order")
    visit_id = fields.Many2one("res.visit", related='sale_id.visit_id')

    def action_post(self):
        vals =super().action_post()
        
        if self.visit_id.sudo():

            trace_obj = self.env['res.traceability'].sudo().search([('sale_visii', '=', self.visit_id.sudo().id)])
           
       
            for f in trace_obj:
                f.invoice_date = datetime.datetime.today()
            if f.invoice_date:
                
                duracion_fecha=  f.invoice_date - f.fecha_visita 
                
                
                
            
                if duracion_fecha.days > 2:
                    duracion_fecha=  str(duracion_fecha.days) + ' Dias' 
                
            
                elif duracion_fecha.seconds <= 172800 and  duracion_fecha.days <= 2:
                    
                    
                    duracion_fecha = duracion_fecha.seconds
                    duracion_fecha_int = round(duracion_fecha / 3600) 
                    if duracion_fecha_int  < 1:
                        duracion_fecha = str(round(duracion_fecha / 60)) + ' Minutos'
                    else:
                        duracion_fecha = str(round(duracion_fecha / 3600)) + ' Horas'

            
                
                # if duracion_fecha.seconds <= 3600:
                #     duracion_minutos=0
                #     duracion_fecha = duracion_fecha.seconds
                #     duracion_fecha = str(round(duracion_fecha / 60)) + ' Minutos'

            # raise UserError(duracion_fecha.days)
                
                 # fecha_total= ((f.fecha_visita.date()) - (f.invoice_date.date())).days
            trace_obj.sudo().write({
                'invoice_date': datetime.datetime.today(),
                'duracion_fecha' : duracion_fecha,
            })    
            
            
        return vals
    
    @api.model
    def create(self,vals):
        res =  super(AccountMoveHeredit, self).create(vals)
        for rec in res:
            if not rec.team_id and rec.invoice_user_id:
                rec.team_id = rec.invoice_user_id.sale_team_id.id if rec.invoice_user_id.sale_team_id else False
            if rec.team_id and rec.invoice_user_id and rec.invoice_user_id.sale_team_id != rec.team_id:
                rec.team_id = rec.invoice_user_id.sale_team_id.id
        return res

