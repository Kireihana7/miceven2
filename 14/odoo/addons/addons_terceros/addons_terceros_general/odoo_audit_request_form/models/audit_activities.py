# -*- coding: utf-8 -*-

from odoo import fields, models

class AuditActivity(models.Model):
    _name = "custom.audit.activity"
    _description = "Actividades de auditorías"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Actividades", tracking=True,)
    
class AuditSpecificAction(models.Model):
    _name = "custom.audit.specific.action"
    _description = "Acciones de auditorías"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Auditorías", tracking=True,)

class AuditMedia(models.Model):
    _name = "custom.audit.media"
    _description = "Medios de verificación de auditorías"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Medios", tracking=True,)