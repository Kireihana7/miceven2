# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from odoo.exceptions import UserError

class ChargueConsolidateReason(models.TransientModel):
    _name="chargue.consolidate.reason"
    _description = "Concepto de Cancelación Romana"

    romana_cancel_reason_id = fields.Many2one("chargue.consolidate.cancel",string= "Motivo de Cancelación de Romana", required =True)
    descripcion = fields.Char(string="Observación",)
    chargue_consolidate = fields.Many2one('chargue.consolidate',string="Orden Asociada",readonly=True,required=True)

    def action_cancelar_manual(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Motivo de Cancelación'),
            'res_model': len(active_ids) == 1 and 'chargue.consolidate.reason' or 'chargue.consolidate.reason',
            'view_mode': 'form',
            'view_id': len(active_ids) != 1 and self.env.ref('eu_agroindustry.view_chargue_consolidate_reason_form').id or self.env.ref('eu_agroindustry.view_chargue_consolidate_reason_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


    def cancel_romana_wizard(self):
        for rec in self:
            if rec.chargue_consolidate:
                rec.chargue_consolidate.romana_cancel_reason_id = rec.romana_cancel_reason_id.id
                rec.chargue_consolidate.descripcion = rec.descripcion
                rec.chargue_consolidate.date_rechazada = fields.Datetime.now()
                rec.chargue_consolidate.approval_rechazada = self.env.uid
                if rec.chargue_consolidate.state == 'por_llegar':
                    rec.chargue_consolidate.state = 'rechazada'
                elif rec.chargue_consolidate.state == 'patio':
                    rec.chargue_consolidate.state = 'por_salir'
                else:
                    rec.chargue_consolidate.state = 'rechazada'

    @api.model
    def default_get(self, default_fields):
        rec = super(ChargueConsolidateReason, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Chequea que venga desde la Orden
        if not active_ids or active_model != 'chargue.consolidate':
            return rec

        chargue_consolidate = self.env['chargue.consolidate'].browse(active_ids)

        # Revisa que exista un resultado en la busqueda, para no permitir crear una cancelación sin consolidado
        if not chargue_consolidate:
            raise UserError(_("Debe tener una Orden para poder cancelar"))
        # Actualiza los campos para la vista
        rec.update({
            'chargue_consolidate': chargue_consolidate[0].id,
        })
        return rec