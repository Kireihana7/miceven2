# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    multi_serie     = fields.Boolean(string="Multiserie company",invisible=True, related="company_id.multi_serie")
    account_serie   = fields.Many2one('account.tipo.serie',string="Tipo de Serie",related="journal_id.account_serie",store=True,readonly=True)
    serie_sequence  = fields.Char(string="Número Serie",readonly=True,default="/",copy=False)
    nro_control     = fields.Char(string='Nro de Control',copy=False, required=False)

    def action_post(self):
        for move in self:
            if move.serie_sequence == '/' and move.account_serie and move.move_type in ('out_invoice','out_refund') and not move.nro_control:
                sequence = move.account_serie.sequence_id if move.move_type == 'out_invoice' else move.account_serie.refund_sequence_id
                s = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                control=self.env['account.tipo.serie.line'].search([('serie_id', '=',move.account_serie.id),('tipo','=','out_invoice')],order="id asc")
                nro_control = self.env['account.tipo.serie.line'].search([('serie_id', '=',move.account_serie.id),('tipo','=','out_invoice')],order="id asc").filtered(lambda lines: lines.actual <= lines.final) or False
                if nro_control:
                    move.nro_control = control.serie_id.code+(str(nro_control[0].actual).zfill(control.serie_id.padding))
                    nro_control[0].actual = nro_control[0].actual + 1
                else:
                    raise UserError('Debe crear un nuevo número de Control para esta serie')
        res = super(AccountMove, self).action_post()
        for move in self:
            if move.journal_id.nota_entrega and move.move_type in ('out_invoice','out_refund') and not move.account_serie:
                move.nro_control = move.name
        return res

    @api.onchange('partner_id')
    def _account_serie_change(self):
        for rec in self:
            rec.account_serie = rec.journal_id.account_serie

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    account_serie = fields.Many2one(related='move_id.account_serie',string="Tipo de Serie",store=True)