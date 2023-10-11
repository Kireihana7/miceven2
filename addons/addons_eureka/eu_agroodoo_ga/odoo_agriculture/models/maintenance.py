# -*- coding: utf-8 -*-

import ast

from datetime import date, datetime, timedelta

from pkg_resources import require

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class MaintenanceStage(models.Model):
    """ Model for case stages. This models the main stages of a Maintenance Request management flow. """
    _inherit = 'maintenance.stage'


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    @api.model
    def default_get(self, fields):
        res = super(MaintenanceRequest, self).default_get(fields)
        res['task_id'] = self.env.context.get('default_task_id')
        res['farmer_request_id'] = self.env.context.get('default_farmer_request_id')
        return res

    # En caso de NO usar la plantilla del cultivo:
    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        required=False,
        tracking=True
    )    

    # En caso de SÍ usar la plantilla del cultivo:
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=False,
        tracking=True
    )    
    
    equipment_reservation_id = fields.Many2one(
        'equipment.reservation',
        string='Equipment Reservation',
        ondelete='cascade',
        required=True,
        tracking=True
    )

    equipment_reservation_line_id = fields.Many2one(
        'equipment.reservation.lines',
        string='Equipment Line',
        ondelete='cascade',
        required=True,
        tracking=True
    )    

    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('equipo_agricola', '=', True)], tracking=True)
    
    price = fields.Float(string='Price', required=True, tracking=True)

    @api.model
    def create(self, vals):
        res = super(MaintenanceRequest, self).create(vals)

        # Verificando si se usó la plantilla de tareas o no:    
        usar_tareas = self.env.context.get('default_usar_tareas')

        id_field_name = 'farmer_request_id'
        id_value = vals.get('farmer_request_id')
        if usar_tareas == True:
            id_field_name = 'task_id'
            id_value = vals.get('task_id')             

        # Último ID del modelo 'maintenance.request':
        maintenance_request_id = self.env['maintenance.request'].search([])[-1].id

        # Insertando datos:
        self.env['crop.request.transaction'].create({
            id_field_name: id_value,
            'maintenance_request_id': maintenance_request_id,
            'type': 'maintenance_request'
        })        
        
        return res   

class MaintenanceTeam(models.Model):
    _inherit = 'maintenance.team'