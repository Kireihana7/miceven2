# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    client_agroupation=fields.Many2one('class.partner.table',string="Clasificación cliente",tracking=True)
    provider_agroupation=fields.Many2one('class.partner.table',string="Clasificación proveedor",tracking=True)
    contact_code=fields.Char("Código interno")

    def name_get(self):
       
            self.browse(self.ids).read(['name', 'cedula','contact_code'])
            return [(template.id, '%s%s - %s' % (template.name and '[%s] ' % template.contact_code or '',template.name,template.cedula or ''))
                        for template in self]



    @api.model
    def _name_search(self, name, args = None, operator = "ilike", limit = 50, name_get_uid = None):
        args = args or []

        domain = [
            *['|'] * 3,
            *map(
                lambda field: (field, operator, name),
                ['name', 'cedula', 'vat','contact_code']
            ),
        ] if name else []

        return self._search(
            domain + args, 
            limit = limit, 
            access_rights_uid = name_get_uid
        )
            # self.browse(self.ids).read(['name'])
            # return [(template.id, '%s' % (template.name and '%s' % template.name or ''))
            #             for template in self]