# -*- coding: utf-8 -*-

from odoo import api, fields, models, _  
from odoo.exceptions import UserError, ValidationError

class AgricultureFincas(models.Model):
    _name = 'agriculture.fincas'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True
    )

    internal_sequence = fields.Char(
        string='Sequence',
        readonly=True,
        tracking=True
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 
        string='Analytic Account',
        # required=True,
        # readonly=True,
        domain=[('num_parents', '=', 0)],
        tracking=True
    )

    partner_id = fields.Many2one('res.partner', string='Farmer', tracking=True)
    partner_ids = fields.Many2many('res.partner', 'finca_partner_rel', 'finca_id', 'partner_id', string='Partner(s)', tracking=True)

    net_area = fields.Float(
        string='Net Area',
        tracking=True
    )

    gross_area = fields.Float(
        string='Gross Area',
        tracking=True
    )        

    farm_type = fields.Selection([
            ('own', 'Own'),
            ('rented', 'Rented')
        ],
        required=True,
        string='Type',
        tracking=True
    ) 

    ubicacion = fields.Text(string='Location', tracking=True)

    unidad_superficie = fields.Selection(
        [
            ('hectare', 'Hectare'),
            ('acre', 'Acre'),
        ],
        string='Surface Unit',
        required=True,
        tracking=True
    )    

    latitud = fields.Char(string='Latitud', tracking=True)
    longitud = fields.Char(string='Longitud', tracking=True)
    altitud = fields.Char(string='Altitud', tracking=True)

    image = fields.Image(string="Image", max_width=1024, max_height=1024, tracking=True)

    # address fields
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    
    finca_coordinate_ids = fields.One2many('agriculture.fincas.coordinates', 'finca_id', string='Farms', tracking=True)

    # ==================================================================================== #
    parcel_ids = fields.One2many('agriculture.parcelas', 'finca_id', string='Parcels', tracking=True)
    parcel_count = fields.Integer(
        compute='_compute_parcel_count',
        string="Parcels",
        tracking=True,
        store=True
    )      

    def action_add_analytic_accounts(self):
        for rec in self:
            farm_id = rec.id
            farm_name = rec.name

            farm_ac_row_count = self.env['account.analytic.account'].search_count([
                ('finca_id', '=', farm_id)
            ])

            if farm_ac_row_count == 0:
                # Creando Centro de Costo para la Finca:
                last_farm_analytic_account_obj = self.env['account.analytic.account'].create({
                    'name': farm_name,
                    'parent_id': False,
                    'is_parent_category': True,
                    # Agriculture:
                    'finca_id': farm_id,
                    # Tipo:
                    'type': 'farm'
                })

                # Asociando la Finca con el Centro de Costo:
                rec.write({
                    'name': farm_name,                
                    'analytic_account_id': last_farm_analytic_account_obj.id
                })

    @api.model
    def create(self, vals): 
        # Asignando secuencia:
        vals['internal_sequence'] = self.env['ir.sequence'].next_by_code('agriculture.fincas')

        # Creando Finca:
        farm = super(AgricultureFincas, self).create(vals)

        # Datos de la Finca recién creada:
        id = farm.id
        internal_sequence = vals['internal_sequence']

        # Creando el Centro de Costo y asociándolo con la Finca:
        last_farm_analytic_account_obj = self.env['account.analytic.account'].create({
            'name': internal_sequence,
            'parent_id': False,
            'is_parent_category': True,
            'finca_id': id,
            'type': 'farm'
        })  

        # Asociando la Finca con el Centro de Costo:
        farm.write({
            'analytic_account_id': last_farm_analytic_account_obj.id
        })

        return farm    

    @api.depends('parcel_ids')
    def _compute_parcel_count(self):
        for rec in self:
            rec.parcel_count = self.env['agriculture.parcelas'].search_count([('finca_id', '=', rec.id)])

    def view_parcels(self):
        action = self.env.ref('odoo_agriculture.action_agriculture_parcelas').read()[0]
        action['domain'] = [('finca_id', '=', self.id)]  
        action['context'] = {
            'default_finca_id': self.id,
        }          
        return action      

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The farm name entered already exists'),
    ]    
    
class AgricultureFincasCoordinates(models.Model):
    _name = 'agriculture.fincas.coordinates'
    _description = 'Coordinates for farms'
    
    latitude = fields.Char(string='Latitude', tracking=True)
    longitude = fields.Char(string='Longitude', tracking=True)
    finca_id = fields.Many2one('agriculture.fincas', string='Farm', tracking=True)