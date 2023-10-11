# -*- coding: utf-8 -*-

from odoo import models, fields, api

DAYS = {
    "0": "Lunes",
    "1": "Martes",
    "2": "Miércoles",
    "3": "Jueves",
    "4": "Viernes",
    "5": "Sábado",
    "6": "Domingo",
}

class ResDay(models.Model):
    _name = "res.day"
    _description = "Dias de la semana"

    name = fields.Selection(list(DAYS.items()), "Dia de la semana")

    @api.depends("name")
    def name_get(self):
        res = super().name_get()

        return [(rec_id, DAYS[rec_name]) for rec_id, rec_name in res]

class ResMonth(models.Model):
    _name = "res.month"
    _description = "Meses"

    name = fields.Selection([
        ("0", "Enero"),
        ("1", "Febrero"),
        ("2", "Marzo"),
        ("3", "Abril"),
        ("4", "Mayo"),
        ("5", "Junio"),
        ("6", "Julio"),
        ("7", "Agosto"),
        ("8", "Septiembre"),
        ("9", "Octubre"),
        ("10", "Noviembre"),
        ("11", "Diciembre"),
    ], "Mes")