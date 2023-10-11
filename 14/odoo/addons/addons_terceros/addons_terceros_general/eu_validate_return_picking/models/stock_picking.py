# -- coding: utf-8 --
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class Picking(models.Model):
    _inherit = "stock.picking"

    is_return = fields.Boolean(string='¿Es una devolución?')
    origin_returned_picking_id = fields.Many2one('stock.picking', string='Origen del picking de devolución')

    def button_validate(self):
        res = super(Picking, self).button_validate()
        # ================ Inicio de Validación ================ #
        if self.is_return: # <----- Validar que sea una devolución.
            # raise UserError(_('SÍ es una devolución.'))
            # Picking Original:
            original_picking = self.env['stock.picking'].search([
                ('id', '=', self.origin_returned_picking_id.id),
                ('state', '=', 'done')
            ])             

            if original_picking:
                # raise UserError(_(f'Picking original: {original_picking.name}.'))
                # Consultando devoluciones realizadas:
                returns = self.env['stock.picking'].search([
                    ('origin', 'ilike', original_picking.name),
                    ('state', '=', 'done')
                ])
                if returns:
                    # raise UserError(_(f'Devoluciones: {returns.mapped("name")}.'))                 
                    # Recorriendo los movimientos del picking original:
                    original_picking_moves = original_picking.move_ids_without_package
                    for origin_picking_move in original_picking_moves:
                        # Cantidad realizada del producto del picking original:
                        quantity_done = origin_picking_move.quantity_done

                        # Movimientos del producto actual de todas las devoluciones:
                        return_product_moves = returns.move_ids_without_package.filtered(lambda m: m.origin_returned_move_id.id == origin_picking_move.id and m.product_id.id == origin_picking_move.product_id.id) 
                        
                        if return_product_moves:      
                            total_qty_returns = sum(return_product_moves.mapped('quantity_done'))
                            
                            available_qty_for_return = quantity_done - total_qty_returns  
                            # raise UserError(_(f'quantity_done: {quantity_done} - total_qty_returns: {total_qty_returns}'))
                            if available_qty_for_return >= 0:
                                if available_qty_for_return > quantity_done:
                                    raise UserError(_(f'La cantidad realizada ({quantity_done}) para el producto {origin_picking_move.product_id.name} es superior a la máxima permitida ({available_qty_for_return}).'))
                            else:   
                                # raise UserError(_(f'quantity_done: {quantity_done} - total_qty_returns: {total_qty_returns}'))
                                raise UserError(_(f'Todas las cantidades del producto {origin_picking_move.product_id.name} han sido devueltas.'))                 
            else:
                raise UserError(_('No se encontró el picking original.'))
        # ================ Fin de Validación ================ #
        
        return res