# -*- coding: utf-8 -*-

from cmath import rect
from multiprocessing.dummy import JoinableQueue
from odoo import api,fields,models,_
from odoo.exceptions import UserError

class GuideConsolidateReprecint(models.Model):
    _name="guide.consolidate.reprecint"
    _description = "Change Precint number"

    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        required=True, 
        default=lambda self: self.env.company.id,
        index=True
    )
    reference = fields.Char(string="Reference",required=True)
    precint_number = fields.Char(string="Precint Number",required=True)
    guide_consolidate = fields.Many2one('guide.consolidate',string="Guide Consolidate",required=True,readonly=True)

    def action_reprecint(self):
        active_ids = self.env.context.get('active_ids')

        if not active_ids:
            return ""

        return {
            'name': _('Change Precint Number'),
            'res_model':'guide.consolidate.reprecint',
            'view_mode': 'form',
            'view_id': self.env.ref('eu_picking_guide.view_guide_consolidate_reprecint_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.model
    def default_get(self, default_fields):
        rec = super().default_get(default_fields)
        active_ids = self._context.get('active_ids', self._context.get('active_id'))
        active_model = self._context.get('active_model')

        # Chequea que venga desde la Orden
        if not active_ids or active_model != 'guide.consolidate':
            return rec

        guide_consolidate = self.env['guide.consolidate'].browse(active_ids)

        # Revisa que exista un resultado en la busqueda, para no permitir crear una carga manual sin guía
        if not guide_consolidate:
            raise UserError(_("Esta función solo sirve para crear un Reprecintado desde una Consolidación"))

        # Actualiza los campos para la vista
        rec.update({
            'guide_consolidate': guide_consolidate[0].id,
            'precint_number': guide_consolidate[0].precint_number,
        })

        return rec

    def reprecint(self):
        for rec in self:
            rec.guide_consolidate.message_post(body=_('El Precinto ha sido modificado por %s. \n Valor Anterior: %s \n Valor actual: %s \n Por Motivo: %s', self.env.user.name,str(rec.guide_consolidate.precint_number),str(rec.precint_number),str(rec.reference)))
            rec.guide_consolidate.write({
                "precint_number": rec.precint_number,
            })

