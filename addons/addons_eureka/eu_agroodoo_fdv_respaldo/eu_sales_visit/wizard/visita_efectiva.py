# -*- coding: utf-8 -*-

import datetime, time 
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VisitaEfectiva(models.TransientModel):
    _name = 'visita.efectiva'
    _description = 'Wizard de visita efectiva'

    visit_id = fields.Many2one(
        "res.visit", 
        default=lambda self: self.env["res.visit"].search([("id", "=", self._context["active_id"])])
    )
    duracion = fields.Float("Duración de la visita")
    note = fields.Char("Nota")

    def action_visita_efectiva(self):
        self.sudo().visit_id.write({
            "duracion": self.duracion,
            "note": self.note,
        })
        self.sudo().visit_id.action_set_status({"status": "efectiva",})
        
            
        self.env['res.traceability'].sudo().create({
            'sale_visii': self.visit_id.id,
            'fecha_visita' : datetime.datetime.today(),
        
        })
        
        
        
        
        return self.sudo().visit_id.action_create_so()
