# -*- coding: utf-8 -*-

from odoo import api,fields,models,_

class ChargueConsolidatExcendente(models.Model):
    _name = "chargue.consolidate.excedente"
    _inherit= ['mail.thread', 'mail.activity.mixin']
    _description = "Excedentes de Romana"

    name = fields.Char(string='Nombre',readonly=True)
    product_id = fields.Many2one('product.template',string="Producto ",readonly=True,tracking=True)
    qty_residual = fields.Float(string="Cantidad Excedente",readonly=True,tracking=True)
    date_empty = fields.Datetime(string="Fecha de Vaciado",readonly=True,tracking=True)
    date_last_full = fields.Datetime(string="Fecha Último Llenado",readonly=True,tracking=True)
    user_empty = fields.Many2one('res.users',string="Usuario que vació",readonly=True,tracking=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    picking_ids = fields.One2many(
        comodel_name='stock.picking',
        inverse_name='chargue_consolidate_excedente',
        string='Entradas Relacionadas',
    )
    # Botón para Cancelar
    def set_empty(self):
        return self.env['chargue.consolidate.excedente.wizard']\
            .with_context(active_ids=self.ids, active_model='chargue.consolidate.excedente', active_id=self.id)\
            .set_empty()

    picking_count = fields.Integer("Movimiento de Inventario", compute='_compute_picking_count')
    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count = self.env['stock.picking'].sudo().search_count([('chargue_consolidate_excedente', '=', rec.id)])

    def open_pickings(self):
        self.ensure_one()
        res = self.env.ref('stock.action_picking_tree_all')
        res = res.read()[0]
        res['domain'] = str([('chargue_consolidate_excedente', '=', self.id)])
        res['context'] = {'create': False}
        return res