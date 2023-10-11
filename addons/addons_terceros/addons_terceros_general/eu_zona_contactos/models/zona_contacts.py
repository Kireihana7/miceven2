
from odoo import models, fields, api

class ZonaContacts(models.Model):
    _name = 'res.partner.zones'
    _inherit=[ 'mail.thread','mail.activity.mixin' ]
    _description='puedes agregar la zona en los contactos'
    

    partner_ids = fields.One2many('res.partner','partner_zone', string="Contacto")
    name = fields.Char(string="Zona",required=True, tracking=True)
    zone = fields.Integer(string="Codigo de Zona", required=True , tracking=True)
    branch_id = fields.Many2one('res.branch', string="Sucursal")
    _sql_constraints=[("zona_uniq", "unique(zone)"," La Zona ya Existe")]

   

    # city_id = fields.Many2one('res.country.state.city', string="Ciudad Zona")
    # _sql_constraints=[("name_uniq", "unique(name)","El no Nombre ya Existe")]
    
    
    # def name_get(self):
    #     result = []
    #     for zona in self:
    #         name = str(zona.name) + ' - ' + str(zona.zone)
    #         result.append((zona.id, name))
    #     return result
#    apellido = fields.Char(compute="_value_pc", store=True)
#    description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
