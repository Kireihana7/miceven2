# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import UserError

class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    audit_id = fields.Many2one('custom.audit.request',string="Auditoría Relacionada",tracking=True)