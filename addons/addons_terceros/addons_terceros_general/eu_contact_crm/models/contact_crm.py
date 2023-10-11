import logging

from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError

from odoo import api, fields, models
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import calendar



_logger = logging.getLogger(__name__)



class PortalWizard(models.TransientModel):

    _name = 'contact.crm.wizard'
    _description = 'Crear Oportunidades'

    def _default_user_ids(self):
        partner_ids = self.env.context.get('active_ids', [])
        contact_ids = set()
        user_changes = []
        for partner in self.env['res.partner'].sudo().browse(partner_ids):
            contact_partners = partner.child_ids.filtered(lambda p: p.type in ('contact', 'other')) | partner
            for contact in contact_partners:
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'monto': '0',
                        'motivo': 'Visita a '+contact.name,
                    }))
        
        return user_changes

    user_ids = fields.One2many('contact.crm.wizard.user', 'wizard_id', string='Users',default=_default_user_ids)

    def action_apply(self):
        self.ensure_one()
        self.user_ids.action_apply()
        return {'type': 'ir.actions.act_window_close'}

class PortalWizardUser(models.TransientModel):

    _name = 'contact.crm.wizard.user'
    _description = 'Configuración CRM'

    wizard_id = fields.Many2one('contact.crm.wizard', string='Wizard', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Contacto', required=True, readonly=True, ondelete='cascade')
    monto = fields.Float('Ingreso Estimado',default='0')
    motivo = fields.Char('Oportunidad',required=True,default='Visita')
    user_id = fields.Many2one('res.users', string='Login User')

    dvisita = fields.Many2one(related='partner_id.dvisita', string='Día de Visita',)
    svisita = fields.Many2many(related='partner_id.svisita', string='Tags',)
    fecha_visita = fields.Date(string='Fecha de Visita', readonly=True, compute='_compute_fecha_visita')
    date_today = fields.Date.today()

    def action_apply(self):
        self.env['res.partner'].check_access_rights('write')
        for wizard_user in self.sudo().with_context(active_test=False):
            user = wizard_user.partner_id.user_ids[0] if wizard_user.partner_id.user_ids else None
            company_id = self.env.company.id
            user_portal = wizard_user.sudo().with_context(company_id=company_id)._create_user()
            wizard_user.refresh()

    #@api.onchange('fecha_visita')
    def _compute_fecha_visita(self):
        
        for rec in self:

            formato = "%d/%m/%Y"
            dia = ''
            if rec.dvisita.numero_dia == 1:     #lunes
                dia = rec.date_today+   relativedelta(weekday=calendar.MONDAY)
            elif rec.dvisita.numero_dia == 2:   #martes
                dia = rec.date_today+   relativedelta(weekday=calendar.TUESDAY)
            elif rec.dvisita.numero_dia == 3:   #miercoles
                dia = rec.date_today+   relativedelta(weekday=calendar.WEDNESDAY)
            elif rec.dvisita.numero_dia == 4:   #jueves
                dia = rec.date_today+   relativedelta(weekday=calendar.THURSDAY)
            elif rec.dvisita.numero_dia == 5:   #viernes
                dia = rec.date_today+   relativedelta(weekday=calendar.FRIDAY)
            elif rec.dvisita.numero_dia == 6:   #sabado
                dia = rec.date_today+   relativedelta(weekday=calendar.SATURDAY)
            elif rec.dvisita.numero_dia == 7:   #domingo
                dia = rec.date_today+   relativedelta(weekday=calendar.SUNDAY)

            rec.fecha_visita = dia
            #raise UserError(rec.dvisita.id)
    
    def _create_user(self):
        company_id = self.env.context.get('company_id')
        return self.env['crm.lead'].create({
            'name': self.motivo,
            'expected_revenue': self.monto,
            'partner_id': self.partner_id.id,
            'company_id': company_id,
            'stage_id': 1,
            'type': 'opportunity',
            'fecha_visita': self.fecha_visita,
        })
