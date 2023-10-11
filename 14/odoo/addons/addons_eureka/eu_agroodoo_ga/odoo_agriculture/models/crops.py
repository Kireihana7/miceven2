# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests

class FarmerLocationCrops(models.Model):
    _name = 'farmer.location.crops'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True
    )

    seed_type_ids = fields.Many2many(
        'seed.type',
        'crop_seed_rel',
        'crop_id',
        'seed_type_id',
        string='Seed Types',
        tracking=True
    )

    default_id = fields.Char(string='Default ID', tracking=True)
    name_en = fields.Char(string='Name', tracking=True)
    name_uk = fields.Char(string='Name', tracking=True)    
    name_ru = fields.Char(string='Name', tracking=True)
    name_pt = fields.Char(string='Name', tracking=True)
    name_es = fields.Char(string='Nombre', tracking=True)
    name_fr = fields.Char(string='Name', tracking=True)
    name_en = fields.Char(string='Name', tracking=True)
    color = fields.Char(string='Color', tracking=True)

    description = fields.Text(
        string='Description',
        tracking=True
    )
    # start_date = fields.Date(
    # 	string='Start Date',
    # 	required=True
    # )
    # end_date = fields.Date(
    # 	string='End Date',
    # 	required=True
    # )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        readonly=True,
        tracking=True
    )

    crop_period_start = fields.Char(
        string='Crop Period Start',
        tracking=True
        # required=True
    )

    crop_period_end = fields.Char(
        string='Crop Period End',
        tracking=True
        # required=True
    )
    crop_task_ids = fields.One2many(
        'crops.tasks.template',
        'crop_id',
        string='Crop Processes',
        tracking=True
    )
    crop_material_ids = fields.One2many(
        'crops.materials.job',
        'crop_id',
        domain=[('internal_type', '=', 'material')],
        string='Crop Materials',
        tracking=True
    )
    crop_labour_ids = fields.One2many(
        'crops.materials.job',
        'crop_id',
        domain=[('internal_type', '=', 'labour')],
        string='Crop Labours',
        tracking=True
    )
    crop_equipment_ids = fields.One2many(
        'crops.materials.job',
        'crop_id',
        domain=[('internal_type', '=', 'equipment')],
        string='Crop Equipments',
        tracking=True
    )    
    crop_overhead_ids = fields.One2many(
        'crops.materials.job',
        'crop_id',
        domain=[('internal_type', '=', 'overhead')],
        string='Crop Overheads',
        tracking=True
    )

    crop_hired_service_ids = fields.One2many(
        'crops.materials.job',
        'crop_id',
        domain=[('internal_type', '=', 'hired_service')],
        string='Crop Overheads',
        tracking=True
    )

    crops_dieases_ids = fields.One2many(
        'crops.dieases',
        'crop_id',
        string='Crop Diseases',
        tracking=True
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        tracking=True
        # required=True
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Stock Location',
        tracking=True
        # required=True
    )
    # image = fields.Binary(
 #        "Image",
 #        attachment=True
 #    )
 
    image = fields.Image(string="Image", max_width=1024, max_height=1024, tracking=True)
    maturities_ids = fields.One2many('farmer.location.crops.maturities', 'crop_id', string='Maturities', tracking=True)
    
    # ==================================================================================== #
    variety_ids = fields.One2many('seed.variety', 'crop_id', string='Varieties', tracking=True)
    variety_count = fields.Integer(
        compute='_compute_variety_count',
        string="Varieties",
        tracking=True
    )           

    # ==================================================================================== #
    crops_dieases_ids = fields.One2many('crops.dieases', 'crop_id', string='Crop Diseases', tracking=True)
    crops_diease_count = fields.Integer(
        compute='_compute_crops_diease_count',
        string="Crop Diseases",
        tracking=True
    )          

    # ==================================================================================== #
    project_count = fields.Integer(
        compute='_compute_project_count',
        string="Project",
        tracking=True
    )               

    @api.depends('project_id')
    def _compute_project_count(self):
        for rec in self:
            rec.project_count = self.env['project.project'].search_count([
                ('crop_id', '=', self.id),
                ('project_template', '=', True)
            ])

    def view_project(self):
        action = self.env.ref('odoo_agriculture.action_view_project_agriculture_template').read()[0]
        action['domain'] = [('crop_id', '=', self.id)]  
        action['context'] = {
            'default_crop_id': self.id
        }          
        return action 

    @api.depends('variety_ids')
    def _compute_variety_count(self):
        for rec in self:
            rec.variety_count = self.env['seed.variety'].search_count([('crop_id', '=', rec.id)])

    def view_varieties(self):
        action = self.env.ref('agrodoo_helper.seed_variety_action').read()[0]
        action['domain'] = [('crop_id', '=', self.id)]  
        action['context'] = {
            'default_crop_id': self.id,
            'hide_crop_id': 1,
        }          
        return action 

    # ==================================================================================== #
    @api.depends('crops_dieases_ids')
    def _compute_crops_diease_count(self):
        for rec in self:
            rec.crops_diease_count = self.env['crops.dieases'].search_count([('crop_id', '=', self.id)])

    def view_dieases(self):
        action = self.env.ref('odoo_agriculture.action_crops_dieases').read()[0]
        action['domain'] = [('crop_id', '=', self.id)]  
        action['context'] = {
            'default_crop_id': self.id,
            'hide_crop_id': 1,
        }          
        return action         
    
    def action_create_crop_project_template(self):
        last_project_created = self.env['project.project'].create({
            'name': f'{self.name_es}',
            'crop_id': self.id,
            'project_template': True
        })
        self.project_id = last_project_created.id   
        
    '''
    def show_json(self):
        crop_data = requests.get('https://crop-monitoring.eos.com/backend/crop-type/?api_key=apk.85114272aff12e873f3d9d209cb1717bbf3e3b53e30d8e6db3c2aefeea3a2661&format=json')
        crop_data = crop_data.json()

        # crop_names = []
        for i, crop in enumerate(crop_data):
            crop_dic = crop_data[i]

            default_id = (crop_dic['id'])
            name_en = (crop_dic['name_en'])
            name_uk = (crop_dic['name_uk'])    
            name_ru = (crop_dic['name_ru'])
            name_pt = (crop_dic['name_pt'])
            name_es = (crop_dic['name_es'])
            name_fr = (crop_dic['name_fr'])
            name_en = (crop_dic['name_en'])
            color = (crop_dic['color'])
            maturities = (crop_dic['maturities'])

            # Insertando datos:
            self.env['farmer.location.crops'].create({
                'default_id': default_id,
                'name_en': name_en,
                'name_uk': name_uk,    
                'name_ru': name_ru,
                'name_pt': name_pt,
                'name_es': name_es,
                'name_fr': name_fr,
                'name_en': name_en,
                'color': color,
            })

            crop_id = self.env['equipment.reservation'].search([])[-1].id
            
            if(len(maturities) > 0):
                for j, maturity in enumerate(maturities):
                    maturity_dic = maturities[j]

                    default_id = maturity_dic['id']
                    name = maturity_dic['name']

                    self.env['farmer.location.crops.maturities'].search([('crop_id', '=', crop_id)]).create({
                        'default_id': default_id,
                        'name': name,                        
                    })

        # raise UserError(_(crop_names))    
    '''

    '''
    _sql_constraints = [
        ('unique_name', 'unique (name)', 'El nombre del cultivo ingresado ya existe'),
    ]    
    '''

class FarmerLocationCropsMaturities(models.Model):
    _name = 'farmer.location.crops.maturities'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    crop_id = fields.Many2one('farmer.location.crops', string="Crop", required=True, tracking=True)
    default_id = fields.Char(string='Default ID', tracking=True)
    name = fields.Char(string='Name', required=True, tracking=True)    