# -*- coding: utf-8 -*-

from odoo import models, fields,api
from odoo.exceptions import AccessError, ValidationError

class ResPartnerSVisita(models.Model):
    _name = 'res.partner.svisita'
    _description = 'Semana de Visita'
    _order = 'id asc'

    name = fields.Char(string='Semana de Visita', required=True, translate=True)
    color = fields.Integer(string='Color Index')
    parent_id = fields.Many2one('res.partner.svisita', string='Parent Category', index=True, ondelete='cascade')
    child_ids = fields.One2many('res.partner.svisita', 'parent_id', string='Child Tags')
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")
    parent_path = fields.Char(index=True)
    partner_ids = fields.Many2many('res.partner', column1='category_id', column2='partner_id', string='Partners')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive tags.'))

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

    dvisita = fields.Many2one(
        'res.partner.dvisita', 
        string='Día de Visita', 
    )

   
    svisita = fields.Many2many('res.partner.svisita', column1='partner_id',
                                    column2='category_id', string='Tags')


class ResPartnerSegmento(models.Model):
    _name = 'res.partner.segmento'
    _description = 'Segmento'
    _order = 'id asc'

    name = fields.Char(
        string='Nombre',
        index=True,
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Este nombre ya existe!"),
    ]
            

class ResPartnerCanal(models.Model):
    _name = 'res.partner.canal'
    _description = 'Canal'
    _order = 'id asc'

    name = fields.Char(
        string='Nombre',
        index=True,
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Este nombre ya existe!"),
    ]


class ResPartnerDVisita(models.Model):
    _name = 'res.partner.dvisita'
    _description = 'Día de Visita'
    _order = 'id asc'

    name = fields.Char(
        string='Nombre',
        index=True,
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Este nombre ya existe!"),
    ]

