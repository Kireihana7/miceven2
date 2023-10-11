# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from werkzeug import urls
import werkzeug

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    partner_id = fields.Many2one(
        'res.partner', string='Contacto', readonly=False)
    input_type = fields.Selection([('manually', 'Manually'), ('link', 'Send Through Email')],
                            string='Tipo de Respuesta', default='manually', required=True, readonly=True)
    
    visit_id = fields.Many2one('res.visit',string = "Visita")

    def survey_user_input_crm(self):
        return {
            'name': 'Survey User_input',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'survey.user_input',
            'view_id': self.env.ref('survey.survey_user_input_view_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
        }

    def survey_resume_answer_crm(self):

        return {
            'type': 'ir.actions.act_url',
            'name': "Resume Survey",
            'target': 'self',
            'url': '/survey/%s/%s' % (self.survey_id.access_token, self.access_token)
        }

    def survey_view_answers_crm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "View Answers",
            'target': 'self',
            'url': '/survey/print/%s?answer_token=%s' % (self.survey_id.access_token, self.access_token)
        }

class ResVisit(models.Model):
    _inherit='res.visit'

    survey_id = fields.Many2one('survey.survey', string="Encuesta", default=lambda self: self.env.company.survey_id)
    survey_user_input_ids = fields.Many2many(
        "survey.user_input", string="Survey User Input Ids", readonly=True,  compute='get_survey_user_input_ids')

    def get_survey_user_input_ids(self):
        if self:
            self.survey_user_input_ids=[]
            survey_user_input_details = self.env['survey.user_input'].sudo().search(
                [('visit_id','=',self.id)], order="id desc")
            if survey_user_input_details:
                self.survey_user_input_ids = survey_user_input_details.ids

    #View/Start Survey
    def action_view_survey(self,answer=None):
        if not self.survey_id or not self.partner_id:
            raise UserError("Please Select Survey Form and Customer.")
        self.ensure_one()
        url = '%s?%s' % (self.survey_id.get_start_url(), werkzeug.urls.url_encode(
            {'answer_token': answer and answer.access_token or None}))

        url += 'partner_id='+str(self.partner_id.id)
        url += '&visit_id='+str(self.id)
        
        

        # print("\n\n\n\n\n kishan URL ==>",url)
        # survey_start_url = werkzeug.urls.url_join(self.survey_id.get_base_url(), self.survey_id.get_start_url()) if self.survey_id else False

        # url = '?partner_id='+str(self.partner_id.id)
        # url += '&visit_id='+str(self.id)
        # survey_start_url = survey_start_url + url
        print("\n\n url ==>", url)
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Survey",
            'target': 'new',
            'url': url,
        }
    #Print Survey    
    def action_view_print_survey(self):
        if not self.survey_id or not self.partner_id:
            raise UserError("Seleccione una Encuesta y un Cliente.")
        return {
            'type': 'ir.actions.act_url',
            'name': "Imprimir Encuesta",
            'target': 'self',
            'url': self.survey_id.with_context(relative_url=True).print_url 
        }
    #Share and invite by email survey
    def action_view_send_survey(self):
        if not self.survey_id or not self.partner_id:
            raise UserError("Seleccione una Encuesta y un Cliente.")
        if (not self.survey_id.page_ids and self.survey_id.questions_layout == 'page_per_section') or not self.survey_id.question_ids:
            raise UserError(
                _('No puedes enviar una invitación de una encuesta sin preguntas.'))
        template = self.env.ref(
            'survey.mail_template_user_input_invite', raise_if_not_found=False)
        local_context = dict(
            self.env.context,
            default_survey_id=self.survey_id.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_survey_start_url=self.survey_id.with_context(
                relative_url=True).public_url + '?partner_id='+str(self.partner_id.id)+'&visit_id='+str(self.id),
            default_partner_ids=[(6, 0, [self.partner_id.id])],
            notif_layout='mail.mail_notification_light',
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'survey.invite',
            'target': 'new',
            'context': local_context,
        }

    #view Result Survey
    def action_view_result_survey(self):

        if not self.survey_id or not self.partner_id:
           raise UserError("Seleccione una Encuesta y un Cliente.")

        return {
            'type': 'ir.actions.act_url',
            'name': "Resultado de la Encuesta",
            'target': 'self',
            'url': self.survey_id.with_context(relative_url=True).result_url
        }

class Partner(models.Model):
    _inherit='res.partner'

    survey_token = fields.Char("survey_token")

class SurveyInvite(models.TransientModel):
    _inherit = 'survey.invite'

    survey_start_url = fields.Char(
        'Survey URL', compute='_compute_survey_start_url')

    @api.depends('survey_id.access_token')
    def _compute_survey_start_url(self):
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        for invite in self:
            if self.env.context.get('default_survey_start_url'):
                invite.survey_start_url = self.env.context.get(
                    'default_survey_start_url')
            else:
                invite.survey_start_url = werkzeug.urls.url_join(
                    base_url, invite.survey_id.get_start_url()) if invite.survey_id else False

class Survey(models.Model):
    _inherit = "survey.survey"

    print_url = fields.Char("Print link", compute="_compute_print_url")
    result_url = fields.Char("Results link", compute="_compute_print_url")
    public_url = fields.Char("Public link", compute="_compute_print_url")

    def _compute_print_url(self):
        """ Computes a public URL for the survey """
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        for survey in self:
            survey.print_url = urls.url_join(
                base_url, "survey/print/%s" % (survey.access_token))
            survey.result_url = urls.url_join(
                base_url, "survey/results/%s" % (survey.id))
            survey.public_url = urls.url_join(
                base_url,"survey/start/%s" % (survey.access_token))

    def _create_answer(self, user=False, partner=False, email=False, test_entry=False, check_attempts=True,visit = False, **additional_vals):
        """ Main entry point to get a token back or create a new one. This method
        does check for current user access in order to explicitely validate
        security.

          :param user: target user asking for a token; it might be void or a
                       public user in which case an email is welcomed;
          :param email: email of the person asking the token is no user exists;
        """

        self.check_access_rights('read')
        self.check_access_rule('read')
        user_inputs = self.env['survey.user_input']
        for survey in self:
            if partner and not user and partner.user_ids:
                user = partner.user_ids[0]

            invite_token = additional_vals.pop('invite_token', False)
            survey._check_answer_creation(
                user, partner, email, test_entry=test_entry, check_attempts=check_attempts, invite_token=invite_token)
            answer_vals = {
                'survey_id': survey.id,
                'test_entry': test_entry,
                'is_session_answer': survey.session_state in ['ready', 'in_progress']
            }
            if survey.session_state == 'in_progress':
                # if the session is already in progress, the answer skips the 'new' state
                answer_vals.update({
                    'state': 'in_progress',
                    'start_datetime': fields.Datetime.now(),
                })
            
            if visit:
                answer_vals['visit_id'] = visit.id

            if partner:
                answer_vals['partner_id'] = partner.id
                partner_obj = self.env['res.partner'].sudo().browse(partner.id)
            elif user and not user._is_public():
                answer_vals['partner_id'] = user.partner_id.id
                answer_vals['email'] = user.email
                answer_vals['nickname'] = user.name
            else:
                answer_vals['email'] = email
                answer_vals['nickname'] = email

            if invite_token:
                answer_vals['invite_token'] = invite_token
            elif survey.is_attempts_limited and survey.access_mode != 'public':
                # attempts limited: create a new invite_token
                # exception made for 'public' access_mode since the attempts pool is global because answers are
                # created every time the user lands on '/start'
                answer_vals['invite_token'] = self.env['survey.user_input']._generate_invite_token(
                )

            answer_vals.update(additional_vals)
            user_inputs += user_inputs.create(answer_vals)
        for question in self.mapped('question_ids').filtered(
                lambda q: q.question_type == 'char_box' and (q.save_as_email or q.save_as_nickname)):
            for user_input in user_inputs:
                if question.save_as_email and user_input.email:
                    user_input.save_lines(question, user_input.email)
                if question.save_as_nickname and user_input.nickname:
                    user_input.save_lines(question, user_input.nickname)

        return user_inputs
