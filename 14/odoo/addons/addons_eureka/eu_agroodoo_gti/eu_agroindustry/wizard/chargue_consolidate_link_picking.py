# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from odoo.exceptions import UserError

class ChargueConsolidateLink(models.Model):
    _name="chargue.consolidate.link.picking"
    _description = "Enlace Picking con PO o SO"

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    operation_type = fields.Selection([
        ('venta', 'Venta'),
        ('compra', 'Compra'),
        ('transferencia', 'Transferencia'),
        ], string='Tipo de Operación' )
    picking_id      = fields.Many2one('stock.picking',string="Picking",domain=[('state','=','done')],readonly=False)
    sale_id         = fields.Many2one('sale.order',string="Orden de Venta",readonly=False)
    purchase_id     = fields.Many2one('purchase.order',string="Orden de Compra",readonly=False)
    chargue_consolidate = fields.Many2one('chargue.consolidate',string="Orden Asociada",readonly=True,required=True)
    
    def action_create_link_picking(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Enlace de Picking'),
            'res_model': len(active_ids) == 1 and 'chargue.consolidate.link.picking' or 'chargue.consolidate.link.picking',
            'view_mode': 'form',
            'view_id': len(active_ids) != 1 and self.env.ref('eu_agroindustry.view_chargue_consolidate_link_form').id or self.env.ref('eu_agroindustry.view_chargue_consolidate_link_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.model
    def default_get(self, default_fields):
        rec = super(ChargueConsolidateLink, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Chequea que venga desde la Orden
        if not active_ids or active_model != 'chargue.consolidate':
            return rec

        chargue_consolidate = self.env['chargue.consolidate'].browse(active_ids)

        # Revisa que exista un resultado en la busqueda, para no permitir crear una carga manual sin consolidado
        if not chargue_consolidate:
            raise UserError(_("Esta función solo sirve para enlazar un Picking desde una Consolidación"))
        # Actualiza los campos para la vista
        rec.update({
            'chargue_consolidate': chargue_consolidate[0].id,
            'operation_type': chargue_consolidate[0].operation_type,
        })
        return rec

    def link_picking(self):
        for order in self:
            if order.operation_type == 'transferencia':
                raise UserError('No se puede enlazar a una PO/SO si es una transferencia')

            consolidate = order.chargue_consolidate

            if order.operation_type == 'venta':
                if len(order.sale_id.order_line) == 1 and len(order.picking_id.move_ids_without_package) == 1:
                    order.picking_id.move_ids_without_package[0].sale_line_id = order.sale_id.order_line[0].id
                    consolidate.sale_ids = [(4, order.sale_id.id, 0)]
                    order.picking_id.chargue_consolidate_create = consolidate.id
                    consolidate.picking_id = [(4, order.picking_id.id, 0)]
                    order.picking_id.vehicle_id = consolidate.vehicle_id.id
                else:
                    raise UserError('Solo debes tener un producto en la SO y en la SU')
            if order.operation_type == 'compra':
                purchase_id = order.purchase_id

                if len(purchase_id.order_line) == 1 and len(order.picking_id.move_ids_without_package.filtered(lambda x: x.state=='done')) == 1:
                    order.picking_id.move_ids_without_package[0].purchase_line_id = purchase_id.order_line[0].id
                    consolidate.purchase_id = purchase_id.id
                    order.picking_id.chargue_consolidate_create = consolidate.id
                    consolidate.picking_id = [(4, order.picking_id.id, 0)]
                    order.picking_id.vehicle_id = consolidate.vehicle_id.id
                else:
                    raise UserError('Solo debes tener un producto en la PO y en la SU')

                return {
                    'name': _('PO'),
                    'res_model': "purchase.order",
                    'res_id': purchase_id.id,
                    'view_mode': 'form',
                    'context': self.env.context,
                    'target': 'current',
                    'type': 'ir.actions.act_window',
                }