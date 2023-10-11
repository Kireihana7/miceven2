# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date, formatLang

from collections import defaultdict
'''
UPDATE: 07-12-2022: Vista que posiblemente genera este error:    
Fields in 'groupby' must be database-persisted fields (no computed fields) -->
'''
# from itertools import groupby
import json

class AssignAgricultureSeqWizard(models.TransientModel):
    _name = 'assign.agriculture.seq.wizard'
    _description = 'Assign Agriculture Sequence'

    model = fields.Selection(
        [
            ('agriculture.fincas', 'Farms'), 
            ('agriculture.parcelas', 'Parcels'),
            ('agriculture.tablon', 'Planks')
        ], 
        required=True, 
        string='Model'
    )

    finca_ids = fields.Many2many('agriculture.fincas', string='Farms')    
    parcel_ids = fields.Many2many('agriculture.parcelas', string="Parcels")    
    tablon_ids = fields.Many2many('agriculture.tablon', string='Planks')

    def action_assign_seq(self):
        data = []
        if self.model == 'agriculture.fincas':
            data = self.finca_ids
        if self.model == 'agriculture.parcelas':
            data = self.parcel_ids
        if self.model == 'agriculture.tablon':
            data = self.tablon_ids   

        if len(data) > 0:
            for line in data:
                internal_sequence = self.env['ir.sequence'].next_by_code(self.model)

                line.update({
                    'internal_sequence': internal_sequence
                })