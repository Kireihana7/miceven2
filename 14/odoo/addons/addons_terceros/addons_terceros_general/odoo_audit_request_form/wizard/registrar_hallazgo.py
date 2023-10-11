# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError

class RegistrarHallazgo(models.TransientModel):
    _name = 'registrar.hallazgo'
    _description = 'Wizard para registrar hallazgos'

    name = fields.Char("Descripción")
    fecha_emision = fields.Date("Fecha del hallazgo", default=fields.Date.context_today)
    user_id = fields.Many2one("res.users", "Responsable", default=lambda self: self.env.user)
    audit_request_id = fields.Many2one("custom.audit.request")
    filename = fields.Char()
    file = fields.Binary("Archivo")

    def action_registar_hallazgo(self):
        CONTEXT = self._context
        AUDIT = self.audit_request_id

        self.env["custom.audit.finding"].create({
            "audit_request_id": AUDIT.id,
            "name": self.name,
            "fecha_emision": self.fecha_emision,
            "user_id": self.user_id.id,
            "filename": self.filename,
            "file": self.file,
        })

        body = """
            <strong>
                Hallazgo registrado en 
                <a href="#" data-oe-model="custom.audit.request" data-oe-id="{id}">{name}</a>:
            </strong>
            <br />
            <i>{content}</i>
        """

        self.env[CONTEXT["default_res_model"]] \
            .sudo() \
            .search([("id", "=", int(CONTEXT["default_res_id"]))]) \
            .message_post(
                is_finding=True,
                body=body.format(
                    id=AUDIT.id,
                    name=AUDIT.name,
                    content=self.name,
                ),
                subject="Registro de auditoría",
            )