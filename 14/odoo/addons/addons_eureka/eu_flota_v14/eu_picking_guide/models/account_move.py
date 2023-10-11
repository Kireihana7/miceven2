# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_type_account = fields.Selection([
        ('facturado', 'Facturado'),
        ('obsequio', 'Obsequio'),
        ('cambio', 'Cambio'),
        ('promo', '¨Promoción'),
        ('saint', 'Pendientes Saint'),
        ], string='Tipo de Factura', copy=False, track_visibility='always', default='facturado')

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_type_account = fields.Selection([
        ('facturado', 'Facturado'),
        ('obsequio', 'Obsequio'),
        ('cambio', 'Cambio'),
        ('promo', '¨Promoción'),
        ('saint', 'Pendientes Saint'),
        ], string='Tipo de Factura', copy=False, track_visibility='always', default='facturado',related="move_id.invoice_type_account",store=True)

    team_id = fields.Many2one(
        related="move_id.team_id",store=True,string="Equipo de Ventas")