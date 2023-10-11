from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
TODAY = date.today()
class HrRenewContract(models.TransientModel):
    _name = 'hr.renew.contract'
    _description="Renueva los ocntratos y los cambia a indefinidos si pasa de dos"

    fecha_ini=fields.Date(required=True,string="Fecha Inicio", default=date.today())
    fecha_final=fields.Date(required=True,string="Fecha Finalizacion")



    def renew(self):
        for rec in self:
            active_ids =self._context.get('active_id')
            active_model = self._context.get('active_model')


            contrato=rec.env[active_model].search([('id','=',active_ids)],limit=1)

            contrato.date_end=rec.fecha_final
            contrato.date_start=rec.fecha_ini
            contrato.number_of_renovations+=1


            # if contrato.number_of_renovations>2:
            #     raise UserError(f"Este contrato presenta {contrato.number_of_renovations} renovaciones, este contrato no puede renovarse, solo volverse fijo.")
            #     contrato.is_indetermined
            
