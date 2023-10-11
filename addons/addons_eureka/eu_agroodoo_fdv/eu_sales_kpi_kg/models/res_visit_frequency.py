# -*- coding: utf-8 -*-

from odoo import models, fields

class MotivoNoVisita(models.Model):
    _name = 'motivo.no.visita'
    _description = 'Motivo de no visita'

    name = fields.Char("Nombre")

class ResVisitFrequency(models.Model):
    _name = 'res.visit.frequency'
    _description = 'Frecuencia de visita'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre", tracking=True)
    repeat_every = fields.Selection([
        ("day", "Dia"),
        ("week", "Semana"),
        ("month", "Mes"),
        ("year", "Año"),
    ], "Repetir cada", default="week", tracking=True,)
    repeat_rate = fields.Integer("Plazo", tracking=True, default=1)
    weekday_ids = fields.Many2many("res.day", "res_visit_res_day_rel", "visit_id", "weekday_id", "Dias", tracking=True,)