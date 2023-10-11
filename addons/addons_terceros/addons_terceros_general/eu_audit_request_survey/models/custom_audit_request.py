# -*- coding: utf-8 -*-

from datetime import date
from odoo import fields, api, models, _
from odoo.exceptions import UserError

class CustomAuditRequest(models.Model):
    _inherit = "custom.audit.request"

    survey_ids = fields.One2many('survey.survey','audit_id',string="CheckList Relacionadas")
    survey_count = fields.Integer(string="CheckList",compute="_compute_survey_count")

    @api.depends('survey_ids')
    def _compute_survey_count(self):
    	for rec in self:
    		rec.survey_count = len(rec.survey_ids)

    def show_survey_survey(self):
        self.ensure_one()
        res = self.env.ref('survey.action_survey_form')
        res = res.read()[0]
        res['domain'] = str([('audit_id', '=', self.id)])
        return res