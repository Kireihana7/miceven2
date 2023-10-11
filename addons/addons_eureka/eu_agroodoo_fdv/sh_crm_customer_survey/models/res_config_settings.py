# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    survey_id = fields.Many2one('survey.survey', string="Encuesta")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    survey_id = fields.Many2one('survey.survey', string="Encuesta", readonly=False, related='company_id.survey_id')
