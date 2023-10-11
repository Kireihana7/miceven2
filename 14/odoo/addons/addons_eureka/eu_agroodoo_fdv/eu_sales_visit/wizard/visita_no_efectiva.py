# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields

class VisitaNoEfectiva(models.TransientModel):
    _name = 'visita.no.efectiva'
    _description = 'Wizard de no visita efectiva'

    state = fields.Selection([
        ("no_visitado", "no_visitado"),
        ("no_efectiva", "No efectiva"),
    ])
    visit_id = fields.Many2one(
        "res.visit", 
        default=lambda self: self.env["res.visit"].search([("id", "=", self._context["active_id"])])
    )
    motivo_cancelacion = fields.Many2one("motivo.no.visita", "Motivo")

    def action_visita_no_efectiva(self):
        self.sudo().visit_id.write({
            "motivo_cancelacion": self.motivo_cancelacion,
            "fecha_cancelacion": date.today(),
        })
        
        self.sudo().visit_id.action_set_status({"status": self.state,})