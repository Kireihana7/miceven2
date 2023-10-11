# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class AgricultureParcelas(models.Model):
    _name = 'agriculture.parcelas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'codigo'

    @api.model
    def default_get(self, fields):
        res = super(AgricultureParcelas, self).default_get(fields)
        res['finca_id'] = self.env.context.get('default_finca_id')
        return res    

    name = fields.Char(
        string='Name',
        required=False,
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
        domain=[('num_parents', '=', 2)],
        tracking=True
    )

    codigo = fields.Char(
        string='Code',
        required=True,
        tracking=True
    )    

    finca_id = fields.Many2one(
        'agriculture.fincas',
        string='Farm',
        required=True,
        tracking=True
    )        

    tipo_suelo_id = fields.Many2one(
        'crops.tipos.suelo',
        string='Soil Type',
        required=True,
        tracking=True
    )        

    metros_cuadrados = fields.Float(
        string='Area',
        required=True,
        tracking=True
    )

    porcentaje_humendad = fields.Float(
        string='Moisture %',
        tracking=True
    )   

    tasa_productividad = fields.Float(
        string='Productivity Rate',
        tracking=True
    )        

    image = fields.Image(string="Image", max_width=1024, max_height=1024, tracking=True)

    parcel_coordinate_ids = fields.One2many('agriculture.parcelas.coordinates', 'parcel_id', string='Parcels', tracking=True)

    # ==================================================================================== #
    tablon_ids = fields.One2many('agriculture.tablon', 'parcel_id', string='Planks', tracking=True)
    tablon_count = fields.Integer(
        compute='_compute_tablon_count',
        string="Planks",
        tracking=True
    )          

    @api.model
    def create(self, vals): 
        # Asignando secuencia:
        vals['internal_sequence'] = self.env['ir.sequence'].next_by_code('agriculture.parcelas')        

        # Creando Parcela:
        parcel = super(AgricultureParcelas, self).create(vals)

        # Datos de la Parcela recién creada:
        id = parcel.id
        internal_sequence = vals['internal_sequence']

        # Creando el Centro de Costo y asociándolo con la Parcela:
        last_parcel_analytic_account_obj = self.env['account.analytic.account'].create({
            'name': internal_sequence,
            'parent_id': parcel.finca_id.analytic_account_id.id,
            'is_parent_category': False,
            'parcel_id': id,
            'type': 'parcel'
        })  

        # Asociando la Parcela con el Centro de Costo:
        parcel.write({
            'analytic_account_id': last_parcel_analytic_account_obj.id
        })

        return parcel    

    def action_add_analytic_accounts(self):
        for rec in self:
            parcel_id = rec.id
            parcel_codigo = rec.codigo
            finca_id = rec.finca_id.id

            parcel_ac_row_count = self.env['account.analytic.account'].search_count([
                ('parcel_id', '=', parcel_id)
            ])

            if parcel_ac_row_count == 0:
                # Creando Centro de Costo para la Parcela:
                last_parcel_analytic_account_obj = self.env['account.analytic.account'].create({
                    'name': parcel_codigo,
                    'parent_id': False,
                    'is_parent_category': False,
                    # Agriculture:
                    'finca_id': finca_id,
                    'parcel_id': parcel_id,
                    # Tipo:
                    'type': 'parcel'
                })
                # Asociando la Parcela con el Centro de Costo:
                rec.write({
                    'name': parcel_codigo,                
                    'analytic_account_id': last_parcel_analytic_account_obj.id
                })


    @api.depends('tablon_ids')
    def _compute_tablon_count(self):
        for rec in self:
            rec.tablon_count = self.env['agriculture.tablon'].search_count([('parcel_id', '=', rec.id)])

    def view_tablones(self):
        action = self.env.ref('odoo_agriculture.action_agriculture_tablon').read()[0]
        action['domain'] = [('parcel_id', '=', self.id)]  
        action['context'] = {
            'default_parcel_id': self.id,
        }          
        return action      

    def name_get(self):        
        list_name = []
        for rec in self:
            record_name = f'[{rec.finca_id.name}] -> {rec.codigo}'
            list_name.append((rec.id, record_name))
        return list_name    

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The parcel name entered already exists'),
        ('unique_codigo', 'unique (codigo)', 'The parcel code entered already exists'),
    ]    

class AgricultureParcelasCoordinates(models.Model):
    _name = 'agriculture.parcelas.coordinates'
    _description = 'Coordinates for parcels'
    
    latitude = fields.Char(string='Latitude', tracking=True)
    longitude = fields.Char(string='Longitude', tracking=True)
    parcel_id = fields.Many2one('agriculture.parcelas', string='Parcel', tracking=True)    