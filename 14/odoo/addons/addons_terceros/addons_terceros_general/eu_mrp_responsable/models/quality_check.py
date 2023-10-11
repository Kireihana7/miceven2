# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class QualityCheck(models.Model):
    _inherit = 'quality.check'

    responsable  = fields.Many2one('hr.employee',string="Responsable",domain="[('reponsable_quality', '=',True)]")
