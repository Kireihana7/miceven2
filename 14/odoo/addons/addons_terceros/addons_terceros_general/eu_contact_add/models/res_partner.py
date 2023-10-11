# -*- coding: utf-8 -*-

from odoo import models, fields,api

# class ResPartnerSVisita(models.Model):
#     _name = 'res.partner.svisita'
#     _description = 'Semana de Visita'
#     _order = 'id asc'

#     name = fields.Char(string='Semana de Visita', required=True, translate=True)
#     color = fields.Integer(string='Color Index')
#     parent_id = fields.Many2one('res.partner.svisita', string='Parent Category', index=True, ondelete='cascade')
#     child_ids = fields.One2many('res.partner.svisita', 'parent_id', string='Child Tags')
#     active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")
#     parent_path = fields.Char(index=True)
#     partner_ids = fields.Many2many('res.partner', column1='category_id', column2='partner_id', string='Partners')

#     @api.constrains('parent_id')
#     def _check_parent_id(self):
#         if not self._check_recursion():
#             raise ValidationError(_('You can not create recursive tags.'))

#     def name_get(self):
#         """ Return the categories' display name, including their direct
#             parent by default.

#             If ``context['partner_category_display']`` is ``'short'``, the short
#             version of the category name (without the direct parent) is used.
#             The default is the long version.
#         """
#         if self._context.get('partner_category_display') == 'short':
#             return super(PartnerCategory, self).name_get()

#         res = []
#         for category in self:
#             names = []
#             current = category
#             while current:
#                 names.append(current.name)
#                 current = current.parent_id
#             res.append((category.id, ' / '.join(reversed(names))))
#         return res
    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    segmento = fields.Many2one(
        'res.partner.segmento', 
        string='Segmento', 
    )

    canal = fields.Many2one(
        'res.partner.canal', 
        string='Canal', 
    )
    codigo_sunagro = fields.Char(string="Código Sunagro")
    #dvisita = fields.Many2one(
    #    'res.partner.dvisita', 
    #    string='Día de Visita', 
    #)

   
    #svisita = fields.Many2many('res.partner.svisita', column1='partner_id',
    #                                column2='category_id', string='Tags')


class ResPartnerSegmento(models.Model):
    _name = 'res.partner.segmento'
    _description = 'Segmento'
    _order = 'id asc'

    name = fields.Char(
        string='Nombre',
        index=True,
    )

class ResPartnerCanal(models.Model):
    _name = 'res.partner.canal'
    _description = 'Canal'
    _order = 'id asc'

    name = fields.Char(
        string='Nombre',
        index=True,
    )


# class ResPartnerDVisita(models.Model):
#     _name = 'res.partner.dvisita'
#     _description = 'Día de Visita'
#     _order = 'id asc'

#     name = fields.Char(
#         string='Nombre',
#         index=True,
#     )

#     numero_dia = fields.Integer(
#         string='Numero de día de la Semana',
#         help='Lunes como primer dia de la Semana debera ser el Nro 1, terminando con el día Domingo a cual le corresponde el Nro 7',
#     )

#     _sql_constraints = [
#         ('name_uniq', 'unique (name)', "name already exists !"),
#         ('numero_dia_uniq', 'unique (numero_dia)', "numero_dia already exists !"),
#         ('numero_dia_min_max', 'CHECK (numero_dia >= 1 AND numero_dia <= 7)', 'El numero debe estar entre 1 y 7.'),

#     ]
