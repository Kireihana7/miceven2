# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError,ValidationError

class ChargueManual(models.Model):
    _name = 'chargue.manual'
    _description ="Contraseña Manual"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre", default='Carga de Peso Manual',readonly=True)
    chargue_consolidate = fields.Many2one('chargue.consolidate',string="Orden Asociada",readonly=True,required=True)
    chargue_state = fields.Selection([
        ('por_llegar', 'Por Llegar'),
        ('patio', 'Patio'),
        ('peso_bruto', 'Peso Bruto'),
        ('peso_tara', 'Peso Tara'),
        ('proceso', 'En Proceso'),
        ('aprobacion', 'Análisis Calidad'),
        ('por_salir', 'Por Salir'),
        ('finalizado', 'Finalizado'),
        ('rechazada', 'Rechazada'),
        ('multi', 'Multi Pesado'),

        ], string='Estatus', readonly=True)

    multi_weight = fields.Many2one('chargue.multi.weight',string="Multi Peso",readonly=True)
    user_id = fields.Many2one('res.users',string="Usuario que aprueba", domain=[('is_romana_admin','=',True)],readonly=True)
    romana_security_pin = fields.Char(string='Contraseña para Romana', size=32,
                                   help='PIN Para colocar el Peso Manual')
    field_to_update = fields.Selection(selection=[
        ('peso_bruto','Peso Bruto'),
        ('peso_bruto_trailer','Peso Bruto Trailer'),
        ('peso_tara','Peso Tara'),
        ('peso_tara_trailer','Peso Tara Trailer')
        ],string="Peso a Actualizar")
    peso_bruto = fields.Selection([
        ('peso_bruto','Peso Bruto'),
        ('peso_bruto_trailer','Peso Bruto Trailer'),
        ],string="Peso a Actualizar",default=''
    )
    peso_tara = fields.Selection([
        ('peso_tara','Peso Tara'),
        ('peso_tara_trailer','Peso Tara Trailer')
        ],string="Peso a Actualizar"
    )
    peso_manual = fields.Float(string="Peso Manual")
    date_manual = fields.Datetime(string="Hora de la Modificación")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,tracking=True,invisible=True)
    def action_register_manual(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Registrar Peso Manual'),
            'res_model': len(active_ids) == 1 and 'chargue.manual' or 'chargue.manual',
            'view_mode': 'form',
            'view_id': len(active_ids) != 1 and self.env.ref('eu_agroindustry.view_register_manual_form').id or self.env.ref('eu_agroindustry.view_register_manual_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    # Función Validar Carga Manual
    def validate(self):
        name = self.env['ir.sequence'].next_by_code('chargue.manual.seq')
        list_user = self.env['res.users'].sudo().search([('is_romana_admin', '=', True)])
        coincide = False
        for user in list_user:
            if self.romana_security_pin == user.romana_security_pin:
                coincide = True
                self.user_id = user.id
        if not coincide:    
            raise UserError('La contraseña no coincide.')
        self.romana_security_pin = ''
        self.name = name
        if self.peso_manual <= 0:
            raise UserError('El Peso Manual debe ser mayor a cero')
        if not self.multi_weight:

            if self.peso_bruto == 'peso_bruto':
                self.chargue_consolidate.peso_bruto = self.peso_manual
                self.chargue_consolidate.date_first_weight = fields.Datetime.now()
            if self.peso_tara == 'peso_tara':
                self.chargue_consolidate.peso_tara = self.peso_manual
                self.chargue_consolidate.date_second_weight = fields.Datetime.now()
            if self.chargue_consolidate.with_trailer:
                if self.peso_bruto == 'peso_bruto_trailer':
                    self.chargue_consolidate.peso_bruto_trailer = self.peso_manual
                if self.peso_tara == 'peso_tara_trailer':
                    self.chargue_consolidate.peso_tara_trailer = self.peso_manual
        if self.multi_weight:
            if self.peso_bruto == 'peso_bruto':
                self.multi_weight.peso_bruto = self.peso_manual
            if self.peso_tara == 'peso_tara':
                self.multi_weight.peso_tara = self.peso_manual
            if self.chargue_consolidate.with_trailer:
                if self.peso_bruto == 'peso_bruto_trailer':
                    self.multi_weight.peso_bruto_trailer = self.peso_manual
                if self.peso_tara == 'peso_tara_trailer':
                    self.multi_weight.peso_tara_trailer = self.peso_manual
            if not self.multi_weight.date_first_weight:
                self.multi_weight.date_first_weight = fields.Datetime.now()
                if self.chargue_consolidate.with_trailer:
                    self.multi_weight.date_first_weight_t = fields.Datetime.now()
            else:
                self.multi_weight.date_second_weight = fields.Datetime.now()
                if self.chargue_consolidate.with_trailer:
                    self.multi_weight.date_second_weight_t = fields.Datetime.now()
        if not self.chargue_consolidate.with_trailer and (self.peso_bruto == 'peso_bruto_trailer' or self.peso_tara == 'peso_tara_trailer'):
            raise UserError('No se puede actualizar el Peso de un remolque si el vehículo no posee uno')

        self.chargue_consolidate.message_post(body=_('El Usuario %s ha actualizado la cantidad manualmente.') % (self.user_id.name,))
        self.date_manual = fields.Datetime.now()
        
    
    @api.model
    def default_get(self, default_fields):
        rec = super(ChargueManual, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        chargue_consolidate = self._context.get('chargue_consolidate')
        active_model = self._context.get('active_model')

        # Chequea que venga desde la Orden
        if not active_ids or active_model != 'chargue.consolidate' and active_model != 'chargue.multi.weight':
            return rec
        if active_model == 'chargue.consolidate':
            chargue_consolidate = self.env['chargue.consolidate'].browse(active_ids)

            # Revisa que exista un resultado en la busqueda, para no permitir crear una carga manual sin consolidado
            if not chargue_consolidate:
                raise UserError(_("Para crear una carga manual, debe hacerlo desde la Orden directamente"))
            # Actualiza los campos para la vista
            rec.update({
                'chargue_consolidate': chargue_consolidate[0].id,
                'chargue_state': chargue_consolidate[0].state,
            })
        if active_model == 'chargue.multi.weight':
            chargue_consolidate = self.env['chargue.consolidate'].browse(chargue_consolidate)
            multi_weight = self.env['chargue.multi.weight'].browse(active_ids)
            # Revisa que exista un resultado en la busqueda, para no permitir crear una carga manual sin consolidado
            if not chargue_consolidate:
                raise UserError(_("Para crear una carga manual, debe hacerlo desde la Orden directamente"))
            # Actualiza los campos para la vista
            rec.update({
                'chargue_consolidate': chargue_consolidate[0].id,
                'chargue_state': chargue_consolidate[0].state,
                'multi_weight': multi_weight[0].id,
            })

        return rec