# -*- coding: utf-8 -*-

import mimetypes
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class Message(models.Model):
    _inherit = 'mail.message'

    is_finding = fields.Boolean()

class CustomAuditFinding(models.Model):
    _name = "custom.audit.finding"
    _description = "Hallazgos de auditorías"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer()
    name = fields.Char("Descripción",tracking=True)
    fecha_emision = fields.Date(
        "Fecha del hallazgo",
        tracking=True, 
        default=fields.Date.context_today
    )
    user_id = fields.Many2one(
        "res.users", 
        "Responsable",
        tracking=True, 
        default=lambda self: self.env.user
    )
    audit_request_id = fields.Many2one("custom.audit.request",tracking=True)
    filename = fields.Char(tracking=True)
    file = fields.Binary("Archivo",tracking=True)
    state = fields.Selection([
        ("enabled", "Habilitado"),
        ("disabled", "Deshabilitado"),
    ], "Estatus", default="enabled", tracking=True)
    to_print = fields.Boolean("Imprimir", tracking=True)
    enabled_reason = fields.Char("Razón para habilitar", tracking=True,)
    disabled_reason = fields.Char("Razón para deshabilitar", tracking=True,)
    is_image = fields.Boolean(compute="_compute_is_image")

    def action_set_state(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Alternar hallazgo",
            "view_mode": "form",
            "res_model": "alternar.hallazgo",
            "target": "new",
            "context": {
                "default_state": self._context["state"],
                "default_parent_id": self.id,
            }
        }

    #region Constrains
    @api.constrains("is_image", "file", "to_print")
    def _check_to_print(self):
        for rec in self:
            if rec.file and rec.to_print and (not rec.is_image):
                raise ValidationError("El archivo no es una imagen ")  

    @api.constrains("file", "filename")
    def _check_file_size(self):
        for rec in self:
            if not rec.file:
                continue
            
            filesize = (len(rec.file) * 3) / 4

            if filesize > 4_194_304:
                raise ValidationError("El archivo no debe exceder 4MB")
    #endregion
       
    @api.depends("file", "filename")
    def _compute_is_image(self):
        for rec in self:
            if not rec.filename:
                rec.is_image = False
                continue

            mimetype = mimetypes.guess_type(rec.filename)[0]

            rec.is_image = False if not mimetype else mimetype.startswith("image")

     
            
                

