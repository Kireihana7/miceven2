# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import fields, api, models, _
from odoo.exceptions import UserError

class CustomAuditRequestObjetives(models.Model):
    _name = "custom.audit.request.objetive"
    _description = "Objetivo de auditoría"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    objetive = fields.Text("Alcance", tracking=True)
    done = fields.Boolean("Realizado", tracking=True)
    audit_request_id = fields.Many2one("custom.audit.request", "Auditoría", tracking=True)
    
class CustomAuditRequest(models.Model):
    _name = "custom.audit.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Audit Request'
    
    name = fields.Char(
        string='Audit Request Name', 
        copy=True,
        required=True,
        tracking=True,
    )
   
    sequence_name = fields.Char(
        string='Audit Request Number', 
        copy=False,
        tracking=True,
    )
    audit_date = fields.Date(
        string='Audit Date', 
        copy=True,
        required=True,
        tracking=True,
    )
    deadline_date = fields.Date(
        string='Deadline Date', 
        copy=True,
        required=True,
        tracking=True,
    )
    responsible_user_id = fields.Many2one(
        'res.users', 
        string='Created by',
        copy=True,
        required=True,
        default=lambda self: self.env.user.id,
        tracking=True,
    )
    audit_responsible_ids = fields.Many2many(
        'hr.employee', 
        'audit_request_employee_rel',
        "audit_request_id", 
        "employee_id", 
        string='Responsables de auditoría',
        copy=True,
        required=True,
        tracking=True,
    )
    approve_user_id = fields.Many2one(
        'res.users', 
        string='Approved by',
        copy=False,
        readonly=True,
        tracking=True,
    )
    refuse_reason = fields.Text(
        string='Reason', 
        copy=False,
        readonly=True,
        tracking=True,
    )
    state = fields.Selection(selection=[
        ('a_draft', 'Draft'),
        ('b_confirm', 'Confirmed'),
        ('c_approve', 'Approved'),
        ('d_done', 'Audit Completed'),
        ('e_cancel', 'Cancelled'),
        ('f_refuse', 'Refused')],
        string='State', 
        copy=False,
        default='a_draft',
        tracking=True,
    )
    
    refuse_user_id = fields.Many2one(
        'res.users', 
        string='Refused by',
        copy=False,
        readonly=True,
        tracking=True,
    )
    date_approve = fields.Date(
        string='Approved Date', 
        copy=False,
        readonly=True,
        tracking=True,
    )
    date_refuse = fields.Date(
        string='Refused Date', 
        copy=False,
        readonly=True,
        tracking=True,
    )
    company_ids = fields.Many2many(
        "res.company", 
        "audit_request_company_rel",
        "audit_request_id",
        "company_id",
        "Empresas",
        tracking=True,
    )
    confirm_user_id = fields.Many2one(
        'res.users', 
        string='Confirmed by',
        copy=False,
        readonly=True,
        tracking=True,
    )
    date_confirm = fields.Date(
        string='Confirmed Date', 
        copy=False,
        readonly=True,
        tracking=True,
    )
    date_done = fields.Date(
        string='Audit Completed Date', 
        copy=False,
        readonly=True,
        tracking=True,
    )
    done_user_id = fields.Many2one(
        'res.users', 
        string='Audit Completed by',
        copy=False,
        readonly=True,
        tracking=True,
    )
    audit_category_id = fields.Many2one(
        'custom.audit.category', 
        string='Audit Category',
        copy=True,
        required=True,
        tracking=True,
    )
    audit_tag_id = fields.Many2one(
        'custom.audit.tag', 
        string='Audit Tags',
        copy=True,
        tracking=True,
    )
    type = fields.Selection(selection=[
        ('internal', 'Internal'),
        ('external', 'External')],
        string='Audit Method', 
        copy=True,
        required=True,
        default='internal',
        tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='External Audit Partner',
        copy=True,
        tracking=True,
    )

    # Campos agregados por Corpoeureka

    audit_finding_ids = fields.One2many(
        "custom.audit.finding",
        "audit_request_id", 
        "Hallazgos", 
        tracking=True,
    )
    audit_activity_id = fields.Many2one(
        "custom.audit.plan.actions",
        "Actividad de auditoría", 
        tracking=True,
    )
    audit_objetives_ids = fields.One2many(
        "custom.audit.request.objetive",
        "audit_request_id",
        "Objetivos", 
        tracking=True,
    )
    audit_status = fields.Selection([
        ("success", "Success"),
        ("warning", "Warning"),
        ("danger", "Danger"),
    ], compute="_compute_audit_status", tracking=True,)
    objetivo = fields.Text("Objetivo", tracking=True,)
    alcance = fields.Text("Criterio", tracking=True,)
    department_id = fields.Many2one(
        "hr.department", 
        "Departamento a auditar", 
        tracking=True,
    )
    department_responsible_id = fields.Many2one(
        "hr.employee", 
        "Responsable del departamento", 
        tracking=True,
    )
    audit_requirements_ids = fields.One2many(
        "custom.audit.requirements", 
        "audit_request_id", 
        "Requerimientos", 
        tracking=True,
    )
    audit_recommendation_ids = fields.One2many(
        "custom.audit.recommendation", 
        "audit_request_id", 
        "Recomendaciones", 
        tracking=True,
    )
        
    @api.depends("audit_date")
    def _compute_audit_status(self):
        for rec in self:
            if not rec.deadline_date:
                continue

            diff = date.today() - rec.deadline_date
            diff = abs(diff.days)
            
            if diff > 7:
                rec.audit_status = "success"
            elif diff > 3:
                rec.audit_status = "warning"
            else:
                rec.audit_status = "danger"

    @api.model
    def create(self, vals):
        vals.update({
            'sequence_name': self.env['ir.sequence'].next_by_code('custom.audit.request')
            })

        res = super().create(vals)

        for rec in res:
            rec.audit_activity_id.audit_request_id = rec

        return res
    
    def unlink(self):
        if any(self.filtered(lambda request: request.state not in ('a_draft', 'e_cancel'))):
            raise UserError(_('You cannot delete a audit request which is not draft or cancelled!'))
        return super(CustomAuditRequest, self).unlink()
            
    def custom_audit_action_reset_draft(self):
        self.state = 'a_draft'
        
    def custom_audit_action_confirm(self):
        self.state = 'b_confirm'
        self.confirm_user_id = self.env.user.id        
        self.date_confirm = fields.Date.today()
        template = self.env.ref('odoo_audit_request_form.custom_email_template_audit_request_confirm_probc', False)
        template.send_mail(self.id)
        
    def custom_audit_action_approve(self):
        self.state = 'c_approve'
        self.approve_user_id = self.env.user.id        
        self.date_approve = fields.Date.today()
        
    def custom_audit_action_done(self):
        self.state = 'd_done'
        self.done_user_id = self.env.user.id        
        self.date_done = fields.Date.today()
        template = self.env.ref('odoo_audit_request_form.custom_email_template_audit_request_done_probc', False)
        template.send_mail(self.id)
        
    def custom_audit_action_cancel(self):
        self.state = 'e_cancel'
        
    def custom_action_audit_send_mail(self):
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
            'default_model': 'custom.audit.request',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            },
        }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: