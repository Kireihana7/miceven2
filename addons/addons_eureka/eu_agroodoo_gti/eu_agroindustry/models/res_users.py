# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = "res.users"

    is_romana_admin = fields.Boolean('¿Puede Establecer el Peso Manual?')
    romana_security_pin = fields.Char(
        'Contraseña para Romana', 
        size=32,
        help='PIN Para colocar el Peso Manual'
    )

    @api.constrains('romana_security_pin')
    def _check_pin(self):
        if self.romana_security_pin and not self.romana_security_pin.isdigit():
            raise UserError(_("El PIN de Seguridad debe contener solo Números"))
