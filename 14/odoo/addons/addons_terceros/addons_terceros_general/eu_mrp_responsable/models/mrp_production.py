# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    responsable  = fields.Many2one('hr.employee',string="Responsable",domain="[('reponsable_production', '=',True)]")
