
from odoo import models, fields, api

class ZonaContacts(models.Model):
    _name = 'res.partner.zones'
    _inherit=[ 'mail.thread','mail.activity.mixin' ]
    _description='puedes agregar la zona en los contactos'
    

    partner_ids = fields.One2many('res.partner','partner_zone', string="Contacto")
    name = fields.Char(string="Zona",required=True, tracking=True)
    zone = fields.Integer(string="Codigo de Zona", required=True , tracking=True)
    _sql_constraints=[("zona_uniq", "unique(zone)"," La Zona ya Existe")]
