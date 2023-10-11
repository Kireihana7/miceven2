# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from email.policy import default
from warnings import WarningMessage
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
'''
UPDATE: 07-12-2022: Vista que posiblemente genera este error:    
Fields in 'groupby' must be database-persisted fields (no computed fields) -->
'''
# from odoo.tools import groupby


class ProductTemplate(models.Model):
    # _name = 'product.template'
    _inherit = 'product.template'

    is_agriculture = fields.Boolean(string='Agriculture', required=True, default=True, tracking=True)
    equipo_agricola = fields.Boolean(string='Agricultural Equipment', tracking=True)
    maintenance_ok = fields.Boolean(string="Can be Maintenance", readonly=True, tracking=True)
    maintenance_as_product = fields.Boolean(string="Maintenance as Product", tracking=True)
    mano_de_obra = fields.Boolean(string='Workforce as Product', tracking=True)
    
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')], string='Product Type', default='product', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.',
        tracking=True)    

    agricultural_internal_type = fields.Selection(
        [
            ('material', 'Material'),
            ('labour', 'Labour'),
            ('equipment', 'Equipment'),
            ('overhead', 'Overhead'),
            ('hired_service', 'Hired Service')
        ],
        string='Agricultural Internal Type',
        # required=True,
        tracking=True
    )            

    # vehicle_ids = fields.Many2many('fleet.vehicle', 'product_vehicle_rel', 'product_id', 'vehicle_id', string='Vehicles')

    @api.onchange('is_agriculture')
    def _onchange_is_agriculture(self):
        # Si se trata de un producto de tipo 'Agricultural Equipment',
        # se le podrá realizar mantenimiento y será un producto de tipo Servicio:
        if self.is_agriculture == False:
            self.equipo_agricola = False
            self.maintenance_ok = False
            self.maintenance_as_product = False
            self.mano_de_obra = False
    
    @api.onchange('equipo_agricola')
    def _onchange_equipo_agricola(self):
        # Si se trata de un producto de tipo 'Agricultural Equipment',
        # se le podrá realizar mantenimiento y será un producto de tipo Servicio:
        self.maintenance_as_product = False
        self.mano_de_obra = False
        if self.equipo_agricola == True:
            self.maintenance_ok = True
            # self.type = 'service'
            self.type = 'product'
        else:
            self.maintenance_ok = False
            self.type = ''

    @api.onchange('maintenance_as_product')
    def _onchange_maintenance_as_product(self):
        # Si se trata de un producto de tipo 'Agricultural Equipment',
        # se le podrá realizar mantenimiento y será un producto de tipo Servicio:
        # self.is_agriculture = True
        self.mano_de_obra = False        
        self.maintenance_ok = False 
        if self.maintenance_as_product == True:
            # self.type = 'service'
            self.type = 'product'
        else:
            self.type = '' 

    @api.onchange('mano_de_obra')
    def _onchange_mano_de_obra(self):
        # Si se trata de un producto de tipo 'Agricultural Equipment',
        # se le podrá realizar mantenimiento y será un producto de tipo Servicio:
        # self.is_agriculture = True
        self.maintenance_as_product = False
        self.maintenance_ok = False        
        if self.mano_de_obra == True:
            # self.type = 'service'
            self.type = 'product'
        else:
            self.type = ''                        

    @api.constrains('maintenance_as_product')
    def _check_maintenance_as_product(self):
        count_maintenance_as_product = self.env['product.template'].search_count([('maintenance_as_product', '=', True)])
        if count_maintenance_as_product != 1:
            raise ValidationError(_('There can only be one Maintenance Product.'))

    @api.constrains('mano_de_obra')
    def _check_mano_de_obra(self):
        count_mano_de_obra = self.env['product.template'].search_count([('mano_de_obra', '=', True)])
        if count_mano_de_obra != 1:
            raise ValidationError(_('There can only be one Workforce Product.'))            
    '''
    @api.model    
    def create(self, vals):
        vals.update({
            'is_agriculture': True
            })
        res = super(ProductTemplate, self).create(vals)
        return res       
    '''

class ProductProduct(models.Model):
    # _name = 'product.product'
    _inherit = 'product.product'
    # _description = 'Product'

    def action_bom_cost_2(self):
        return True

