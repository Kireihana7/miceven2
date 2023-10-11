# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_nucleo = fields.Boolean("Es nucleo", tracking=True)
    codigo_nucleo = fields.Char("Código nucleo", tracking=True)

    @api.onchange("is_nucleo")
    def _onchange_is_nucleo(self):
        self.update({"codigo_nucleo": False})

    @api.onchange("company_type")
    def _onchange_type_nucleo(self):
        self.update({"is_nucleo": False})
    
class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    from_nucleo = fields.Boolean("Propiedad de nucleo", tracking=True)

    @api.onchange("vehicle_type_property")
    def _onchange_vehicle_type_property(self):
        self.update({"from_nucleo": False})

    @api.onchange("from_nucleo")
    def _onchange_from_nucleo(self):
        if self.from_nucleo:
            return {
                "domain": {
                    "vehicle_owner": [('is_nucleo','=',True)]
                }
            }

class ChargueConsolidate(models.Model):
    _inherit = "chargue.consolidate"

    cosecha_manual = fields.Boolean(tracking=True)
    cosecha_mecanizada = fields.Boolean(tracking=True)
    cosecha_verde = fields.Boolean(tracking=True)
    cosecha_quemada = fields.Boolean(tracking=True)
    lote = fields.Char()
    tablon = fields.Char()
