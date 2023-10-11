# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.

from odoo import models, fields

class CustomAuditRefuseWizard(models.TransientModel):
    _name = 'alternar.hallazgo'
    _description = 'Alternar el estado de los hallazgos'

    state = fields.Selection([
        ("enabled", "Habilitado"),
        ("disabled", "Deshabilitado"),
    ], "Estatus", default="enabled",)
    enabled_reason = fields.Char("Razón para habilitar",)
    disabled_reason = fields.Char("Razón para deshabilitar",)
    parent_id = fields.Many2one("custom.audit.finding")

    def action_alternar_hallazgo(self):
        self.parent_id.write({
            "state": self.state,
            "enabled_reason": self.enabled_reason,
            "disabled_reason": self.disabled_reason,
        })

        body = """
            <strong>
                <a href="#" data-oe-model="custom.audit.finding" data-oe-id="{id}">
                    Hallazgo
                </a>
                fue {state} por {username}
            </strong>
        """

        body=body.format(
            id=self.parent_id.id,
            state=("habilitado" if self.state == "enabled" else "deshabilitado"),
            username=self.env.user.name,
        )

        self.parent_id \
            .message_post(
                body=body,
                subject="Cambio de estado en hallazgo",
            )

        self.parent_id \
            .audit_request_id \
            .message_post(
                body=body,
                subject="Cambio de estado en hallazgo"
            )