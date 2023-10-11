# -*- coding: utf-8 -*-

from odoo import fields, models

class CustomAuditRequirements(models.Model):
    _name = "custom.audit.requirements"
    _description = "Requerimientos de auditorías"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Requerimiento", tracking=True,)
    status = fields.Selection([
        ("en_proceso", "En proceso"),
        ("completado", "Completado"),
    ], default="en_proceso", tracking=True,)
    is_conforme = fields.Boolean("Conforme", tracking=True,)
    audit_request_id = fields.Many2one("custom.audit.request", "Auditoria", tracking=True)

class CustomAuditRecommendation(models.Model):
    _name = "custom.audit.recommendation"
    _description = "Recomendaciones de auditorías"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Recomendación", tracking=True,)
    department_id = fields.Many2one("hr.department", "Área de departamento", tracking=True,)
    checked = fields.Boolean("Chequeada", tracking=True,)
    audit_request_id = fields.Many2one("custom.audit.request", "Auditoria", tracking=True)