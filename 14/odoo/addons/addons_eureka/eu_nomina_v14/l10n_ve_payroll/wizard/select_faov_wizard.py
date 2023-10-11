from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange


class FaovDateSelect(models.TransientModel):
    
    _name="faov.date.select"
    _description="Modelo transitorio para reportes de FAOV y MINTRA"
    fecha=fields.Date('Indique mes y año')
    def get_actives(self):
        if self._context.get('active_ids'):
            return self.env['hr.employee'].search([('id','in',self._context.get('active_ids'))])
        else:
            return self.env['hr.employee'].search([('id','=',self._context.get('active_id'))])

    def export_faov(self):

        employee_ids='_'.join(map(str,self.get_actives().ids))
        
        return {
            'type'  : 'ir.actions.act_url',
            'url'   : f"/faov/{self.fecha.strftime('%d-%m-%Y')}/{employee_ids}",
            'target': 'new',
            'res_id': self.ids,
            
        }
    def export_mintra_fijo(self):
        employee_filtered=self.get_actives().filtered(lambda x:(not x.fecha_inicio or x.fecha_inicio<self.fecha) and (not x.fecha_fin or x.fecha_fin>self.fecha))

        employee_ids='_'.join(map(str,employee_filtered.ids))
        
        return {
            'type'  : 'ir.actions.act_url',
            'url'   : f"/mintraf/{employee_ids}",
            'target': 'new',
            'res_id': self.ids,
            
        }
    def export_mintra_variable(self):
        employee_filtered=self.get_actives().filtered(lambda x:(not x.fecha_inicio or x.fecha_inicio<self.fecha) and (not x.fecha_fin or x.fecha_fin>self.fecha))

        employee_ids='_'.join(map(str,employee_filtered.ids))
        
        return {
            'type'  : 'ir.actions.act_url',
            'url'   : f"/mintrav/{employee_ids}",
            'target': 'new',
            'res_id': self.ids,
            
        }

    