# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class AgricultureTablon(models.Model):
    _name = 'agriculture.tablon'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'codigo'

    @api.model
    def default_get(self, fields):
        res = super(AgricultureTablon, self).default_get(fields)
        res['parcel_id'] = self.env.context.get('default_parcel_id')
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
        domain=[('num_parents', '=', 3)],
        tracking=True
    )

    codigo = fields.Char(
        string='Code',
        required=True,
        tracking=True
    )    

    parcel_id = fields.Many2one(
        'agriculture.parcelas',
        string='Parcel',
        required=True,
        tracking=True
    )        

    area = fields.Float(
        string='Area',
        required=True,
        tracking=True
    )

    image = fields.Image(string="Image", max_width=1024, max_height=1024, tracking=True)

    tablon_coordinate_ids = fields.One2many('agriculture.tablon.coordinates', 'tablon_id', string='Planks', tracking=True)

    @api.model
    def create(self, vals): 
        # Asignando secuencia:
        vals['internal_sequence'] = self.env['ir.sequence'].next_by_code('agriculture.tablon')        

        # Creando Tablón:
        tablon = super(AgricultureTablon, self).create(vals)

        # Datos de la Tablón recién creada:
        id = tablon.id
        internal_sequence = vals['internal_sequence']

        # Creando el Centro de Costo y asociándolo con el Tablón:
        last_tablon_analytic_account_obj = self.env['account.analytic.account'].create({
            'name': internal_sequence,
            'parent_id': tablon.parcel_id.analytic_account_id.id,
            'is_parent_category': False,
            'tablon_id': id,
            'type': 'plank'
        })  

        # Asociando el Tablón con el Centro de Costo:
        tablon.write({
            'analytic_account_id': last_tablon_analytic_account_obj.id
        })

        return tablon    

    def action_add_analytic_accounts(self):
        for rec in self:
            plank_id = rec.id
            plank_codigo = rec.codigo     
            # Parcela:
            parcel_id = rec.parcel_id.id
            # Finca
            finca_id = self.env['agriculture.parcelas'].search([
                ('id', '=', parcel_id)
            ]).finca_id.id    

            plank_ac_row_count = self.env['account.analytic.account'].search_count([
                ('tablon_id', '=', plank_id)
            ])                                   

            if plank_ac_row_count == 0:
                # Centro de Costo del Tablón:
                parcel_analytic_account_obj = rec.parcel_id.analytic_account_id

                # Creando Centro de Costo para el Tablón:
                last_plank_analytic_account_obj = self.env['account.analytic.account'].create({
                    'name': plank_codigo,
                    'parent_id': parcel_analytic_account_obj.id,
                    'is_parent_category': False,
                    # Agriculture:
                    'finca_id': finca_id,
                    'parcel_id': parcel_id,                                    
                    'tablon_id': plank_id,
                    # Tipo:
                    'type': 'plank'
                })
                # Asociando el Tablón con el Centro de Costo:
                rec.write({
                    'name': plank_codigo,                
                    'analytic_account_id': last_plank_analytic_account_obj.id
                })                    

    def name_get(self):        
        list_name = []
        for rec in self:
            record_name = f'[{rec.parcel_id.finca_id.name}] -> [{rec.parcel_id.codigo}]-> {rec.codigo}'
            list_name.append((rec.id, record_name))
        return list_name

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The parcel name entered already exists'),
        ('unique_codigo', 'unique (codigo)', 'The parcel code entered already exists'),
    ]    

class AgricultureTablonCoordinates(models.Model):
    _name = 'agriculture.tablon.coordinates'
    _description = 'Coordinates for planks'
    
    latitude = fields.Char(string='Latitude', tracking=True)
    longitude = fields.Char(string='Longitude', tracking=True)
    tablon_id = fields.Many2one('agriculture.tablon', string='Plank', tracking=True)        