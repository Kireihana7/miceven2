# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class SaleOrderVentas(models.Model):
    _inherit = 'crm.lead'

    segmento = fields.Many2one(
        'res.partner.segmento', 
        string='Segmento', 
        readonly=1,
    )

    canal = fields.Many2one(
        'res.partner.canal', 
        string='Canal', 
        readonly=1,
    )
    dvisita = fields.Many2one(
        'res.partner.dvisita', 
        string='Día de visita', 
        readonly=1,
    )

    svisita = fields.Many2many('res.partner.svisita', column1='partner_id',
                                    column2='category_id', string='Semana de Visita',readonly=1,)

    @api.onchange('partner_id')
    def onchange_partner_id_canal(self):

        if not self.partner_id:
            self.update({
                'canal': False,
                'segmento': False,
                'dvisita': False,
                'svisita': False,
            })
            return

        values = {
            'canal': self.partner_id.canal,
            'segmento': self.partner_id.segmento,
            'dvisita': self.partner_id.dvisita,
            'svisita': self.partner_id.svisita,
        }
        self.update(values)