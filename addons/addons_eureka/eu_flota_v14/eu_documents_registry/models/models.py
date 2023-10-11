# -*- coding: utf-8 -*-

from datetime import date
from dateutil.relativedelta import relativedelta 
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartnerDocument(models.Model):
    _name = "res.partner.document"
    _description = "Registro de documentos"

    name = fields.Char("Tipo de documento")

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if self.search([("id", "!=", rec.id),("name", "=", rec.name.lower())]):
                raise ValidationError("Ese documento ya está registrado")

class DocumentMixin(models.AbstractModel):
    _name = "document.mixin"
    _description = "Mixin para lineas de documentos"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    document_id = fields.Many2one("res.partner.document", "Tipo de documento")
    name = fields.Char("Documento", related="document_id.name")
    code = fields.Char("Código")
    due_date = fields.Date("Fecha de expiración")
    emit_date = fields.Date("Fecha de emisión")

    @api.constrains("due_date", "emit_date")
    def _check_dates(self):
        for rec in self:
            if rec.due_date < rec.emit_date:
                raise ValidationError("Las fechas son inválidas")

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if self.search([("code", "=", rec.code),("id", "!=", rec.id)]):
                raise ValidationError("El código ya se encuentra registrado")

class ResPartnerDocumentLine(models.Model):
    _name = "res.partner.document.line"
    _description = "Documentos del contacto"
    _inherit = "document.mixin"

    def _action_notify_due(self):
        self.env["res.partner.document.line"] \
            .search([("due_date", "<=", fields.Date.to_string(date.today() - relativedelta(days=5)))]) \
            ._notify_expiration()

    partner_id = fields.Many2one("res.partner", "Contacto")

    def _notify_expiration(self):
        for rec in self.sudo():
            rec.activity_schedule(
                "eu_documents_registry.mail_activity_due_document",
                date.today(),
                summary="Un documento está cerca de vencerse",
                note=f"El documento {rec.name} de {rec.partner_id.name}",
                user_id=self.env.user.id,
                request_partner_id=rec.partner_id.id,
            )

class ResPartner(models.Model):
    _inherit = "res.partner"

    document_ids = fields.One2many("res.partner.document.line", "partner_id", "Documentos")

    @api.constrains("document_ids")
    def _check_document_ids(self):
        for rec in self:
            documents = rec.document_ids

            if len(documents.mapped("document_id.id")) != len(documents):
                raise ValidationError("Los documentos deben ser únicos")