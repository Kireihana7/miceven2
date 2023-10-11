from odoo import models, fields, api

class CompanySequence(models.Model):
    _inherit="res.company"

    maintenance_sequence = fields.Many2one('ir.sequence', string="Secuencia del Mantenimiento")