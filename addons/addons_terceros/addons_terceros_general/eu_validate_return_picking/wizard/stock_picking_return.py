# -- coding: utf-8 --
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        # TODO sle: the unreserve of the next moves could be less brutal
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()
        
        origin_returned_picking_ids = []
        for return_line in self.product_return_moves:
            return_line.move_id.id
            # Agregando ID del Picking de origen:
            # raise UserError(_(f'ID de Picking de origen: {return_line.move_id.picking_id.id}.'))    
            origin_returned_picking_ids.append(return_line.move_id.picking_id.id)            

            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed."))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                # ================ Inicio de Validación ================ #
                # Consultando si ya se han realizado devoluciones:
                returns = self.env['stock.picking'].search([
                    ('origin', 'ilike', self.picking_id.name),
                    ('state', '=', 'done')
                ])
                # Cantidad:
                quantity_done = return_line.move_id.quantity_done

                if returns:
                    # raise UserError(_('Ya se han realizado devoluciones'))
                    # Obteniendo el total de las cantidades de las devoluciones del producto:
                    moves = returns.move_ids_without_package.filtered(lambda m: m.origin_returned_move_id.id == return_line.move_id.id and m.product_id.id == return_line.product_id.id) 
                    if moves:
                        # raise UserError(_(f'Hay movimientos ({moves}) para el producto {return_line.product_id.name}.'))
                        total_qty_returns = sum(moves.mapped('quantity_done'))
                        available_qty_for_return = quantity_done - total_qty_returns
                        # raise UserError(_(f'Cantidad máxima permitida para devolver: {available_qty_for_return}.'))
                        if available_qty_for_return > 0:
                            if return_line.quantity > available_qty_for_return:
                                # raise UserError(_(f'La cantidad ingresada ({return_line.quantity}) para el producto {return_line.product_id.name} es superior a la máxima permitida ({available_qty_for_return}).'))
                                raise UserError(_(f'La cantidad ingresada ({return_line.quantity}) para el producto {return_line.product_id.name} es superior a la máxima permitida ({available_qty_for_return}).'))
                        else:
                            raise UserError(_(f'Todas las cantidades del producto {return_line.product_id.name} han sido devueltas.'))           
                else:
                    # raise UserError(_('No se han realizado devoluciones.'))
                    if return_line.quantity > quantity_done:
                        raise UserError(_('La cantidad debe ser menor o igual al del picking original.'))
                # ================ Fin de Validación ================ #

        # Herencia
        new_picking, pick_type_id = super(ReturnPicking, self)._create_returns()
        
        # Estableciendo el picking original y el valor para determinar que es una devolución:
        self.env['stock.picking'].search([('id', '=', new_picking)]).write({
            'is_return': True,
            'origin_returned_picking_id': origin_returned_picking_ids[0]
        })
        
        return new_picking, pick_type_id