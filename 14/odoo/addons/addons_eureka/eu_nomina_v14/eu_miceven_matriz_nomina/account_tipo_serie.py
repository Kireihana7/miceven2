# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountTipoSerie(models.Model):
    _name = 'account.tipo.serie'
    _description = "Tipo de Serie Facturación"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre de la Serie',required=True,copy=False)
    code = fields.Char('Código de la Serie',required=True,help="Este campo es el PREFIJO que mostrará la serie",copy=False)
    padding= fields.Integer("Cantidad de digitos en la secuencia",required=True,copy=False)
    sequence_id = fields.Many2one('ir.sequence',string="Secuencia",readonly=False,copy=False)
    refund_sequence_id = fields.Many2one('ir.sequence',string="Secuencia Nota de Crédito",readonly=False,copy=False)
    serie_id = fields.One2many('account.tipo.serie.line','serie_id',string="Números Asociados",copy=False)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company,readonly=True,invisible=True)

    @api.model
    def _get_sequence_prefix(self, code, refund=False):
        prefix = code.upper()
        if refund:
            prefix = 'R' + prefix
        return prefix
        
    @api.model
    def _create_sequence(self, vals, refund=False):
        prefix = self._get_sequence_prefix(vals['code'], refund)
        seq_name = refund and vals['name'] + _(': Refund') or vals['name']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': vals.get('padding',4),
            'number_increment': 1,
            'use_date_range': False,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        return seq

    @api.model
    def create(self, vals):
        if not vals.get('sequence_id'):
            vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
        if not vals.get('refund_sequence_id'):
            vals.update({'refund_sequence_id': self.sudo()._create_sequence(vals, refund=True).id})
        serie = super(AccountTipoSerie, self.with_context(mail_create_nolog=True)).create(vals)
        return serie


class AccountTipoSerieLine(models.Model):
    _name = 'account.tipo.serie.line'
    _description = "Tipo de Serie Facturación Línea"


    serie_id = fields.Many2one('account.tipo.serie',string="Tipo de Serie")
    begin = fields.Integer(string="Número Inicial",required=True)
    final = fields.Integer(string="Número Final",required=True)
    tipo = fields.Selection([('out_invoice', 'Factura de Cliente'), ('out_refund', 'Nota de Crédito Cliente')],string="Tipo de Serie",required=True)
    actual = fields.Integer(string="Número Actual",readonly=True,force_save=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company,readonly=True,invisible=True)
    finalizado = fields.Boolean(default=False,compute="_compute_finalizado",readonly=True)

    @api.depends('actual','final')
    def _compute_finalizado(self):
        for rec in self:
            rec.finalizado = True if rec.actual >= rec.final else False

    @api.constrains('actual')
    def constrains_actual(self):
        for rec in self:
            if rec.actual > rec.final + 1:
                raise UserError('El número actual no puede ser mayor al número final')

    @api.constrains('final')
    def constrains_final(self):
        for rec in self:
            if rec.begin > rec.final:
                raise UserError('El número inicial no puede ser mayor al número final')
            if rec.begin == rec.final:
                raise UserError('El número inicial no puede ser igual al número final')

    @api.onchange('begin')
    def _onchange_begin(self):
        for rec in self:
            rec.actual = rec.begin

    def unlink(self):
        for rec in self:
            if rec.finalizado:
                raise UserError('No puede eliminar un registro que ya tenga Facturas')
        res = super(AccountTipoSerieLine,self).unlink()

    @api.model
    def create(self, vals):
        #raise UserError(vals.get('begin'))
        if vals.get('begin') and vals.get('serie_id'):
            for rec in self.env['account.tipo.serie.line'].search([]):
                if vals.get('begin') <= rec.final and vals.get('begin') >= rec.begin:
                    raise UserError('No puede crear un registro que ya esté en el rango ')
        serie = super(AccountTipoSerieLine, self).create(vals)            
        return serie

    def write(self, vals):
        #raise UserError(vals.get('begin'))
        if vals.get('begin'):
            for rec in self.env['account.tipo.serie.line'].search([]):
                if vals.get('begin') <= rec.final and vals.get('begin') >= rec.begin:
                    raise UserError('No puede crear un registro que ya esté en el rango ')
        serie = super(AccountTipoSerieLine, self).write(vals)            
        return serie