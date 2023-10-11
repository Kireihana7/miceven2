# -*- coding: utf-8 -*-

from datetime import date
from odoo import fields, models, api
from odoo.exceptions import UserError

class AuditPlanObservation(models.Model):
    _name = "custom.audit.plan.observation"
    _description = "Observaciones de planificacion de auditoría"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Observación", tracking=True)
    audit_plan_id = fields.Many2one("custom.audit.plan", "Planificación", tracking=True)

class AuditPlan(models.Model):
    _name = "custom.audit.plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Planificación de auditorías"

    name = fields.Date("Fecha", tracking=True, default=fields.Date.context_today)
    title = fields.Char("Nombre", tracking=True,)
    responsible_id = fields.Many2one("hr.employee", "Responsable", tracking=True,)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, tracking=True)
    observation_ids = fields.One2many("custom.audit.plan.observation", "audit_plan_id", "Observaciones", tracking=True,)
    objetivo_general = fields.Text("Objectivo general", tracking=True,)
    audit_action_ids = fields.One2many("custom.audit.plan.actions", "audit_plan_id", "Acciones", tracking=True,)
    status = fields.Selection([
        ("revision","Revision"),
        ("modificar","Modificar"),
        ("rechazado","Rechazado"),
        ("aprobado","Aprobado"),
    ], "Estatus", default="revision", tracking=True)
 
    def action_set_status(self, context: dict={}):
        self.write({"status": self._context.get("status") or context.get("status")})

    def name_get(self):
        res = super().name_get()

        for id, name in res:
            rec = self.filtered(lambda r: r.id == id)

            if rec.name and rec.title:
                name = " ".join(filter(bool, [str(rec.name), rec.title]))
        
        return res

    def action_send_mail(self):
        self.ensure_one()

        ir_model_data = self.env['ir.model.data']

        try:
            template_id = ir_model_data.get_object_reference('odoo_audit_request_form', 'custom_email_send_template_all_audit_request_state_probc')[1]
        except ValueError:
            template_id = False

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': {
                'default_model': 'custom.audit.plan',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
            },
        }

    def write(self, vals):
        if (not self.user_has_groups("odoo_audit_request_form.audit_manager_group")) and ("status" in vals):
            raise UserError("No tienes permisos para establecer el estado de la planificación")

        return super().write(vals)
