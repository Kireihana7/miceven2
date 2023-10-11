# -*- coding: utf-8 -*-
  
from odoo import fields, models
from odoo.exceptions import UserError

class EosModel(models.AbstractModel):
    _name = "eos.model"
    _description = "Modelo de EOS"

    eos_id = fields.Integer('ID de EOS')
    version = fields.Integer('Version')

    def get_eos_url(self) -> str:
        pass

    def action_fetch_from_eos(self):
        pass
    
    def action_delete_from_eos(self):
        pass

    def get_header(self):
        key = self.get_key()

        return {
            "Authorization": f"ApiKey {key}",
        }

    def get_key(self) -> str:
        KEY =  self.env['ir.config_parameter'] \
            .sudo() \
            .get_param('eu_eos_integration.api_eos_key')

        if not KEY:
            raise UserError("No tienes ninguna llave de API de EOS registrada")

        return KEY

    def unlink(self):
        if any(rec.eos_id for rec in self):
            raise UserError("No puedes borrar un modelo sin haberlo eliminado de EOS primero")
            
        return super().unlink()