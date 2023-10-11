# -*- coding: utf-8 -*-

from datetime import date
from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError

class AuditPlanDocumentation(models.Model):
    _name ="custom.audit.documentation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Documentación de auditorias"

    name = fields.Char("Documentación", tracking=True,)
    accorded = fields.Boolean("Conforme", tracking=True,)
    not_accorded = fields.Boolean("Inconforme", tracking=True,)
    audit_action_id = fields.Many2one("custom.audit.plan.actions", "Acción de planificación", tracking=True)
    checked = fields.Boolean("Revisado", tracking=True,)
    observation = fields.Char("Observación", tracking=True,)

    @api.constrains("accorded","not_accorded",)
    def _check_according(self):
        for rec in self:
            if rec.accorded and rec.not_accorded:
                raise ValidationError("No puedes estar conforme e inconforme a la vez")

    @api.onchange("checked")
    def _onchange_checked(self):
        for rec in self:
            rec.update({
                "accorded": False,
                "not_accorded": False,
            })

class AuditPlanActions(models.Model):
    _name = "custom.audit.plan.actions"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Acciones de la planificación de auditorias"

    memo_sequence = fields.Char("Sequencia de memo", tracking=True)
    name = fields.Date("Fecha", tracking=True,)
    audit_plan_id = fields.Many2one("custom.audit.plan", "Plan de auditoria", ondelete="cascade", tracking=True,)
    company_ids = fields.Many2many(
        "res.company", 
        "audit_actions_company_rel",
        "action_id",
        "company_id",
        "Empresas",
        tracking=True,
    )
    responsible_ids = fields.Many2many(
        "hr.employee", 
        "custom_audit_plan_actions_employee_rel",
        "audit_plan_actions_id",
        "employee_id",
        "Responsables de auditoría", 
        tracking=True,
    )
    audit_activity_id = fields.Many2one("custom.audit.activity", "Actividad a realizar", tracking=True,)
    audit_request_id = fields.Many2one("custom.audit.request", "Auditoria", tracking=True)
    audit_media_ids = fields.Many2many(
        "custom.audit.media",
        "audit_actions_media_rel",
        "action_id",
        "media_id",
        "Medios de verificación",
        tracking=True,
    )
    audit_documentation_ids = fields.One2many("custom.audit.documentation", "audit_action_id", "Documentación", tracking=True)
    audit_specific_action_ids = fields.Many2many(
        "custom.audit.specific.action",
        "audit_actions_specific_action_rel",
        "action_id",
        "specific_action_id",
        "Acciones específicas",
        tracking=True,
    )
    branch_ids = fields.Many2many(
        "res.branch",
        "audit_actions_branch_rel",
        "action_id",
        "branch_id",
        "Sucursales",
        tracking=True,
    )
    lapse_start = fields.Datetime("Inicio del periodo", tracking=True,)
    lapse_end = fields.Datetime("Culminación del periodo", tracking=True,)
    duration_start = fields.Datetime("Inicio de auditoría", tracking=True,)
    duration_end = fields.Datetime("Culminación de la auditoría", tracking=True,)
    status = fields.Selection([
        ("success", "Success"),
        ("warning", "Warning"),
        ("danger", "Danger"),
    ], compute="_compute_status", tracking=True)
    done = fields.Boolean("Realizado", tracking=True, store=True, compute="_compute_done")

    @api.depends("audit_request_id.state")
    def _compute_done(self):
        for rec in self:
            rec.done = rec.audit_request_id.state == "d_done"

    @api.depends("name")
    def _compute_status(self):
        for rec in self:
            if not rec.name:
                continue
            
            diff = date.today() - rec.name
            diff = abs(diff.days)
            
            if diff > 7:
                rec.status = "success"
            elif diff > 3:
                rec.status = "warning"
            else:
                rec.status = "danger"

    #region Actions
    def action_create_audit_request(self):
        self.ensure_one()

        if self.audit_plan_id.status != "aprobado":
            raise UserError(
                "No puedes crear una auditoría si el plan no está aprobado"
            )

        return {
            'type': 'ir.actions.act_window',
            'res_model': "custom.audit.request",
            'view_mode': 'form',
            'target': 'current',
            'context': {
                "default_audit_activity_id": self.id,
                "default_deadline_date": self.duration_end.date(),
                "default_company_ids": self.company_ids.ids,
                "default_audit_responsible_ids": self.responsible_ids.ids,
            },
        }

    def action_open_audit_memo_report(self):
        return self.env \
            .ref("odoo_audit_request_form.custom_action_report_audit_memo") \
            .report_action(self)
    #endregion

    @api.model
    def create(self, vals):
        res = super().create(vals)

        for rec in res:
            rec.memo_sequence = self.env['ir.sequence'].next_by_code('custom.audit.plan.actions')

        return res

    def get_departments_logos(self):
        return self.env['hr.department'] \
            .search([('is_audit_department',"=",True), ('image_128', '!=', False)]) \
            .mapped('image_128')
    
    def action_send_memo_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('odoo_audit_request_form', 'custom_email_send_template_all_audit_memo_probc')[1]
        except ValueError:
            template_id = False

        ctx = dict()
        ctx.update({
            'default_model': 'custom.audit.plan.actions',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })

        # breakpoint()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }
