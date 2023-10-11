from datetime import date
from odoo import models, fields, api

class InHeritDocumentFechaAlerta(models.Model):
    _inherit = 'documents.document'

    fecha_alerta= fields.Date(string="Fecha de Alerta", tracking=True)
    notificado = fields.Boolean(string="Vencimiento notificado")

    def crear_alerta(self):
        if self.fecha_alerta and self.fecha_alerta < fields.Date.today() and not self.notificado:
            self.notificado = True
            self.activity_schedule(
                act_type_xmlid="eu_document_fecha_alerta.vista_fecha_alerta_activity",
                date_deadline=date.today(),
                summary="¡Documentos Vencidos!",
                note=f"¡Tienes documentos vencidos por revisar!",
                user_id=self.owner_id.id,
                request_partner_id=self.owner_id.partner_id.id
            )
        if self.notificado and self.fecha_alerta and self.fecha_alerta > fields.Date.today():
            self.notificado = False
    @api.model        
    def _action_fecha_alerta(self):
        document = self.env['documents.document'].sudo().search([])
        for rec in document:
            rec.crear_alerta()