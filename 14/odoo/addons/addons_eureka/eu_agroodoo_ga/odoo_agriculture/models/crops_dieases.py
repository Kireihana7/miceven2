# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class CropsDieases(models.Model):
    _name = 'crops.dieases'
    # _rec_name = 'crops_dieases_cure_id'

    @api.model
    def default_get(self, fields):
        res = super(CropsDieases, self).default_get(fields)
        res['crop_id'] = self.env.context.get('default_crop_id')
        return res    

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True
    )

    causal_agent = fields.Char(
        string='Causal Agent',
        required=False,
        tracking=True
    )	

    source = fields.Selection([
            ('mushroom', 'Mushroom'),
            ('virus', 'Virus'),
            ('bacterium', 'Bacterium'),
        ],
        required=False,
        string='Source',
        tracking=True
    ) 

    current_impact = fields.Selection([
            ('XXXX', 'XXXX'),
            ('XXX', 'XXX'),
            ('XX', 'XX'),
            ('X', 'X'),
            ('(-)', '(-)'),
            ('Escape', 'Escape'),
        ],
        required=False,
        string='Current Impact',
        tracking=True,
        help='''
            XXXX ---> Muy importante
            XXX ---> Medianamente importante
            XX ---> Importante
            X ---> Poco Importante
            (-) ---> Sin importancia
            Escape ---> Es cuando una planta se le dan las condiciones de manejo y nutrición adecauda para que ella se defienda de las enfermedades.
        '''
    )     

    description = fields.Text(
        string='Description',
        required=False,
        tracking=True
    )
    crops_dieases_cure_id = fields.Many2one(
        'crops.dieases.cure',
        string="Crops Dieases Cure",
        tracking=True
    )
    crop_id = fields.Many2one(
        'farmer.location.crops',
        string="Crop",
        required=True,
        tracking=True
    )

    image = fields.Image(string="Image", max_width=1024, max_height=1024, tracking=True)

    '''
    @api.onchange('crops_dieases_cure_id')
    def onchange_crops_dieases_cure_id(self):
        if self.crops_dieases_cure_id:
            self.description = self.crops_dieases_cure_id.description	
    '''


class CropsDieasesCure(models.Model):
    _name = 'crops.dieases.cure'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True
    )
    description = fields.Text(
        string='Description',
        required=False,
        tracking=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


