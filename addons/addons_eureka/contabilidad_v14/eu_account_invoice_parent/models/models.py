# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from pytz import timezone
from odoo.exceptions import UserError

class AccountMoveCreditMotivo(models.Model):
    _name = 'account.move.credit.motivo'
    _description = 'Motivo de Nota de Crédito'
    _order = 'id desc'

    name = fields.Char(
        string='Nombre',
        index=True,
    )

class AccountMove(models.Model):
    _inherit = 'account.move'

    parent_id = fields.Many2one('account.move', string='Factura Padre', index=True)
    children_ids = fields.One2many('account.move','parent_id', string='Factura Hijas', index=True)
    num_credit = fields.Char(string="Número de Nota de Crédito")
    ref_credit = fields.Char(string="Nro Control Nota de Crédito")
    motivos = fields.Many2one('account.move.credit.motivo', string='Motivo', index=True)
    with_nc = fields.Boolean(string='¿Tiene Nota de Crédito?', default=False,readonly=True)
    parent_count = fields.Integer("Notas de Crédito", compute='_compute_payment_count')

    def show_parent_invoice(self):
        return {
            'name': _('Nota de Crédito'),
            'view_mode': 'tree',
            'res_model': 'account.move',
            'view_id': False,
            'views': [(self.env.ref('account.view_move_tree').id, 'tree')],
            'type': 'ir.actions.act_window',
            'domain': [('parent_id', '=', self.id)],
            'context': {'create': False},
        }
    def _compute_payment_count(self):
        for move in self:
            move.parent_count = self.env['account.move'].search_count([('parent_id', '=', move.id)])

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'
    
    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        res.update({'parent_id': move.id,'invoice_user_id':move.invoice_user_id.id})
        return res 