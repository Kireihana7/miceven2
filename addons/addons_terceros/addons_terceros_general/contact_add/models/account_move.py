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
        #compute="_onchange_partner_id_canal",
        readonly=1,
        store=True,
    )

    dvisita = fields.Many2one(
        'res.partner.dvisita', 
        string='Día de Visita',
        readonly=1, 
    )
    svisita = fields.Many2many('res.partner.svisita', column1='partner_id',
                                    column2='category_id', string='Semana de Visita',readonly=1,)

    # @api.depends('partner_id')
    # def _onchange_partner_id_canal(self):
    #     if not self.partner_id:
    #         self.canal = False
    #         self.segmento = False
    #         self.dvisita = False
    #         self.svisita = False
    #     else:
    #         self.canal = self.partner_id.canal
    #         self.segmento = self.partner_id.segmento
    #         self.dvisita = self.partner_id.svisita
    #         self.svisita = self.partner_id.dvisita
