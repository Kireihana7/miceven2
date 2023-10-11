# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    price_per_hour_use = fields.Float(string='Price per hour of use', required=True)
    hourmeter_count = fields.Integer(compute="_compute_hourmeter_count", string='Hourmeter')

    def _compute_hourmeter_count(self):
        for rec in self:
            rec.hourmeter_count = self.env['fleet.vehicle.hourmeter'].search_count([('vehicle_id', '=', rec.id)])

    def view_hourmeter(self):
        action = self.env.ref('odoo_agriculture.fleet_vehicle_hourmeter_action').read()[0]
        action['domain'] = [('vehicle_id', '=', self.id)]  
        action['context'] = {
            'default_vehicle_id': self.id
        }          
        return action         

class FleetVehicleHourmeter(models.Model):
    _name = 'fleet.vehicle.hourmeter'
    _description = 'Hour meter log for a vehicle'
    _order = 'date desc'

    name = fields.Char(compute='_compute_vehicle_log_name', store=True)
    date = fields.Date(default=fields.Date.context_today)
    value = fields.Float('Hourmeter Value', group_operator="    ")
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True)
    # unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True)
    driver_id = fields.Many2one(related="vehicle_id.driver_id", string="Driver", readonly=False)

    @api.depends('vehicle_id', 'date')
    def _compute_vehicle_log_name(self):
        for record in self:
            name = record.vehicle_id.name
            if not name:
                name = str(record.date)
            elif record.date:
                name += ' / ' + str(record.date)
            record.name = name

    '''
    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.unit = self.vehicle_id.odometer_unit        
    '''