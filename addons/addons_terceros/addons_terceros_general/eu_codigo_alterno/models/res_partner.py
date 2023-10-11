
from odoo import models, fields, api

class InheritCodigoAlterno(models.Model):
    _inherit = 'res.partner'


    alternate_code = fields.Char(string="Codigo Alterno", tracking=True)

    
