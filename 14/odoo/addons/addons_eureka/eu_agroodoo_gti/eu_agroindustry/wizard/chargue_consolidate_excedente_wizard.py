# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from odoo.exceptions import UserError
class ChargueConsolidateExcedenteWizard(models.TransientModel):
    _name="chargue.consolidate.excedente.wizard"
    _description = "Concepto de Cancelación Romana"




    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    chargue_excedente = fields.Many2one('chargue.consolidate.excedente',string="Excedente")
    name = fields.Char(string='Nombre',readonly=True)
    product_id = fields.Many2one('product.template',string="Producto ",readonly=True)
    product_uom = fields.Many2one(related='product_id.uom_id',string="Unidad de Medida")
    product_uom_qty = fields.Float(string="Cantidad",readonly=False)
    location_dest_id = fields.Many2one(
        'stock.location', "Ubicación de Destino",
        domain="[('usage', '=', 'internal')]",
        check_company=True,)

    def set_empty(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Entrada de Inventario'),
            'res_model': len(active_ids) == 1 and 'chargue.consolidate.excedente.wizard' or 'chargue.consolidate.excedente.wizard',
            'view_mode': 'form',
            'view_id': len(active_ids) != 1 and self.env.ref('eu_agroindustry.view_chargue_consolidate_excedente_wizard_form').id or self.env.ref('eu_agroindustry.view_chargue_consolidate_excedente_wizard_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


    @api.model
    def default_get(self, default_fields):
        rec = super(ChargueConsolidateExcedenteWizard, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Chequea que venga desde la Orden
        if not active_ids or active_model != 'chargue.consolidate.excedente':
            return rec

        chargue_consolidate_excedente = self.env['chargue.consolidate.excedente'].browse(active_ids)

        if not chargue_consolidate_excedente:
            raise UserError(_("Esta función sirve solo para dar ingreso a los Excedentes"))
        # Actualiza los campos para la vista
        rec.update({
            'chargue_excedente': chargue_consolidate_excedente[0].id,
            'product_uom_qty': chargue_consolidate_excedente[0].qty_residual,
            'product_id':chargue_consolidate_excedente[0].product_id.id,
            'name':'Ingreso de %s' % chargue_consolidate_excedente[0].name,
        })
        return rec

    def _get_stock_type_ids(self):
        data = self.env['stock.picking.type'].search([])
        for line in data:
            if line.code == 'incoming':
                return line



    picking_type_id = fields.Many2one('stock.picking.type', 'Tipo de Operación',default=_get_stock_type_ids,
        domain="[('code', '=', 'incoming')]")

    def create_picking(self):
        if self.product_uom_qty > self.chargue_excedente.qty_residual:
            raise UserError('No puedes dar ingreso más de lo que está disponible')
        if self.product_uom_qty == 0:
            raise UserError('La cantidad a ingresar no puede ser cero.')
        if self.chargue_excedente.qty_residual == 0:
            raise UserError('La cantidad excedente es cero, por lo que no hay nada para ingresar.')
        if not self.picking_type_id:
            raise UserError(_(
                " Por favor, seleccione un tipo de operación"))
        pick = {}
        location_id = self.env['stock.location'].search([('usage','=','customer')],limit=1).id
        if self.picking_type_id.code == 'incoming':
            pick = {
                'picking_type_id': self.picking_type_id.id,
                'origin': 'Ingreso por Excedente',
                'location_dest_id': self.picking_type_id.default_location_dest_id.id,
                'location_id': location_id,
                'chargue_consolidate_excedente': self.chargue_excedente.id,
            }
        picking = self.env['stock.picking'].create(pick)

        moves = self._create_stock_moves(picking)
        move_ids = moves._action_confirm()
        move_ids._action_assign()
        self.chargue_excedente.qty_residual -= self.product_uom_qty
        self.chargue_excedente.date_empty = fields.Datetime.now()
        self.chargue_excedente.user_empty = self.env.uid

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        location_id = self.env['stock.location'].search([('usage','=','customer')],limit=1).id
        for line in self:
            if picking.picking_type_id.code == 'incoming':
                template = {
                    'name': self.name or '',
                    'product_id': line.product_id.product_variant_id.id,
                    'product_uom': line.product_uom.id,
                    'location_id': location_id,
                    'location_dest_id': picking.picking_type_id.default_location_dest_id.id,
                    'picking_id': picking.id,
                    'state': 'draft',
                    'company_id': self.env.company.id,
                    'price_unit': line.product_id.standard_price,
                    'picking_type_id': picking.picking_type_id.id,
                    'route_ids': 1 and [
                        (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
            diff_quantity = line.product_uom_qty
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            template['product_uom_qty'] = diff_quantity
            done += moves.create(template)
        return done