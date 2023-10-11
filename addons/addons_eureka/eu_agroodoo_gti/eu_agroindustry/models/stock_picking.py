# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    seed_type_id = fields.Many2one("seed.type", "Tipo de semilla")

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    seed_type_id = fields.Many2one("seed.type", "Tipo de semilla", related="move_id.seed_type_id")

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    location_dest_id = fields.Many2one(states={
        'confirmed': [('readonly', False)], 
        'draft': [('readonly', False)]
    })
    chargue_consolidate = fields.Many2many('chargue.consolidate', 'Orden de Transferencia',compute="_compute_chargue_consolidate_count")
    consolidate_status = fields.Selection(related="chargue_consolidate.state", string='Estatus')
    chargue_consolidate_create = fields.Many2one('chargue.consolidate', 'Orden Romana')
    chargue_consolidate_excedente = fields.Many2one('chargue.consolidate.excedente','Entrada por Excedente')
    chargue_consolidate_descuento = fields.Many2one('chargue.consolidate.descuento','Entrada por Descuento')
    chargue_consolidate_count = fields.Integer("Ordenes de Carga", compute='_compute_chargue_consolidate_count')

    def _compute_chargue_consolidate_count(self):
        for rec in self:
            rec.chargue_consolidate = self.env['chargue.consolidate'] \
                .sudo() \
                .search([('picking_id', 'in', [rec.id])])
            rec.chargue_consolidate_count=len(rec.chargue_consolidate)

    def open_chargue_consolidate(self):
        self.ensure_one()

        res = self.env.ref('eu_agroindustry.open_chargue_consolidate_without')
        res = res.read()[0]
        res['domain'] = str([('picking_id', 'in', self.ids)])

        return res

    @api.onchange("chargue_consolidate")
    def _onchange_chargue_consolidate(self):
        vehicles = self.chargue_consolidate.vehicle_id.ids

        if vehicles:
            self.update({"vehicle_id": vehicles[0]})

    vehicle_id = fields.Many2one('fleet.vehicle', "Vehículo", tracking=True)
    vehicle_type_property = fields.Selection(related='vehicle_id.vehicle_type_property',store=True)
    driver_id = fields.Many2one('res.partner', "Conductor",readonly=False)
    license_plate = fields.Char("Licencia", related="vehicle_id.license_plate",store=True)
    country_id = fields.Many2one('res.country', default=lambda self: self.env['res.country'].search([('code','=','VE')]), invisible=True)
    state_id = fields.Many2one("res.country.state", 'Estado', domain="[('country_id', '=?', country_id)]")
    city_id = fields.Many2one('res.country.state.city', 'Ciudad', domain="[('state_id','=',state_id),('country_id','=',country_id)]")