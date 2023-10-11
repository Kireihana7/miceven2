# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class SaleOrderVentas(models.Model):
    _inherit = 'account.move'

    segmento = fields.Many2one(
        'res.partner.segmento', 
        string='Segmento', 
        readonly=1,
    )

    canal = fields.Many2one(
        'res.partner.canal', 
        string='Canal', 
        compute="_onchange_partner_id_canal",
        readonly=1,
    )

    # dvisita = fields.Many2one(
    #     'res.partner.dvisita',
    #     string='Día de Visita',
    #     readonly=1, 
    # )
    # svisita = fields.Many2many('res.partner.svisita', column1='partner_id',
    #                                 column2='category_id', string='Semana de Visita',readonly=1,)

    @api.depends('partner_id')
    def _onchange_partner_id_canal(self):
        for rec in self:
            if not rec.partner_id:
                rec.update({
                    'canal': False,
                    'segmento': False,
                    #'dvisita': False,
                    #'svisita': False,
    #                'fecha_visita': False,
                })
                return

            values = {
                'canal': rec.partner_id.canal,
                'segmento': rec.partner_id.segmento,
                #'svisita': self.partner_id.svisita,
                #'dvisita': self.partner_id.dvisita,
    #            'fecha_visita': self.partner_id.fecha_visita,
            }
            rec.update(values)