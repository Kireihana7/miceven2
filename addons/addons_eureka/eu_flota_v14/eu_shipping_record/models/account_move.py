# -*- coding: utf-8 -*-

from odoo import models, fields

VALS = {
    "invoice_id": None, 
    "state": "finalizado",
}

class AccountMove(models.Model):
    _inherit = 'account.move'

    fleet_trip_id_ids = fields.One2many("fleet.trip", "invoice_id", "Viaje asociado", tracking=True,)

    def button_draft(self):
        super().button_draft()

        self.fleet_trip_id_ids.write(VALS)
        
    def button_cancel(self):
        super().button_cancel()

        self.fleet_trip_id_ids.write(VALS)