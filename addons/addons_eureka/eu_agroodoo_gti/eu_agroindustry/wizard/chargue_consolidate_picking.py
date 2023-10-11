# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from odoo.exceptions import UserError

class ChargueConsolidatePicking(models.Model):
    _name="chargue.consolidate.picking"
    _description = "Creación de Picking desde Carga"

    def _get_stock_type_ids(self):
        domain = []

        if self.chargue_consolidate.operation_type == 'venta':
            domain.append(("code", "=", "outgoing"))
        elif self.chargue_consolidate.operation_type == 'compra':
            domain.append(("code", "=", "incoming"))
        else:
            domain.append(("code", "=", "internal"))

        return self.env['stock.picking.type'].search(domain, limit=1)

    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        required=True, 
        default=lambda self: self.env.company.id,
        index=True
    )
    descripcion = fields.Char(string="Observación")
    chargue_consolidate = fields.Many2one('chargue.consolidate',string="Orden Asociada",readonly=True,required=True)
    operation_type = fields.Selection([
        ('venta', 'Venta'),
        ('compra', 'Compra'),
        ('transferencia', 'Transferencia'),
    ], string='Tipo de Operación', copy=False, index=True, tracking=True, default='')
    partner_id = fields.Many2one('res.partner',string="Contacto")
    scheduled_date = fields.Datetime(string="Fecha Programada",default=lambda self: fields.Datetime.now(),)
    product_id = fields.Many2one('product.product',string="Producto",domain="[('need_romana','=',True)]")
    product_uom = fields.Many2one(related='product_id.uom_id',string="Unidad de Medida")
    product_uom_qty = fields.Float(string="Cantidad Solicitada",readonly=True)
    location_src_id = fields.Many2one(
        'stock.location', "Ubicación de Origen",
        check_company=True,)
    location_dest_id = fields.Many2one(
        'stock.location', "Ubicación de Destino",
        check_company=True,)
    seed_type_id = fields.Many2one("seed.type", "Tipo de semilla")
    owner_id = fields.Many2one('res.partner', 'Propietario',)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 
        'Tipo de Operación',
        default=_get_stock_type_ids,
        domain="[('code', 'in', {'venta': ['outgoing'], 'compra': ['incoming'], 'transferencia': ['internal']}.get(operation_type, []))]")
    purchase_id = fields.Many2one("purchase.order", "Compra")
    sale_id = fields.Many2one("sale.order", "Venta")

    def action_create_picking(self):
        active_ids = self.env.context.get('active_ids')

        if not active_ids:
            return ""

        return {
            'name': _('Creación de Picking'),
            'res_model':'chargue.consolidate.picking',
            'view_mode': 'form',
            'view_id': self.env.ref('eu_agroindustry.view_chargue_consolidate_picking_form').id,
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
        if not active_ids or active_model != 'chargue.consolidate':
            return rec

        chargue_consolidate = self.env['chargue.consolidate'].browse(active_ids)

        # Revisa que exista un resultado en la busqueda, para no permitir crear una carga manual sin consolidado
        if not chargue_consolidate:
            raise UserError(_("Esta función solo sirve para crear un Picking desde una Consolidación"))
        if not chargue_consolidate[0].vehicle_id:
            raise UserError(_('Debes asignar un vehículo antes de crear el Picking'))

        # Actualiza los campos para la vista
        rec.update({
            "chargue_consolidate": chargue_consolidate[0].id,
            "operation_type": chargue_consolidate[0].operation_type,
            "partner_id":  chargue_consolidate[0].partner_id.id,
        })

        return rec

    @api.onchange("operation_type")
    def _onchange_operation_type(self):
        field = "purchase_id" if self.operation_type == "compra" else "sale_id"
        consolidate = self.chargue_consolidate

        return {
            "domain": {
                field: [("id", "in", consolidate.purchase_id.ids if "purchase" in field else consolidate.sale_ids.ids)]        
            }
        }

    def create_picking(self):
        for rec in self:
            if not rec.picking_type_id:
                raise UserError(_(" Por favor, seleccione un tipo de operación"))

            rec.chargue_consolidate.picking_id = False

            origin = rec.chargue_consolidate.name

            if rec.chargue_consolidate.purchase_id:
                origin = rec.chargue_consolidate.purchase_id.name 
            elif rec.chargue_consolidate.sale_ids:
                origin = ", ".join(rec.chargue_consolidate.sale_ids.mapped("name")) 

            if not rec.chargue_consolidate.picking_id:
                vals = {
                    'picking_type_id': rec.picking_type_id.id,
                    'vehicle_id': rec.chargue_consolidate.vehicle_id.id,
                    'partner_id': rec.partner_id.id,
                    'owner_id': rec.owner_id.id,
                    'origin': origin,
                    'chargue_consolidate_create': rec.chargue_consolidate.id,
                }

                if rec.picking_type_id.code == 'outgoing':
                    vals.update({
                        'location_dest_id': rec.partner_id.property_stock_customer.id,
                        'location_id': rec.picking_type_id.default_location_src_id.id,
                    })
                elif rec.picking_type_id.code == 'incoming':
                    vals.update({
                        'location_dest_id': rec.picking_type_id.default_location_dest_id.id,
                        'location_id': rec.partner_id.property_stock_supplier.id,
                    })
                elif rec.picking_type_id.code == 'internal':
                    vals.update({
                        'location_id': rec.location_src_id.id,
                        'location_dest_id': rec.location_dest_id.id,
                    })

                picking = rec.env['stock.picking'] \
                    .sudo() \
                    .with_context({"chargue_consolidate": self.chargue_consolidate.id}) \
                    .create(vals)

                rec.chargue_consolidate.picking_id = picking or False

                move_ids = rec \
                    ._create_stock_moves(picking) \
                    ._action_confirm()

                move_ids._action_assign()

                if rec.sale_id and rec.chargue_consolidate.operation_type == 'venta':
                    move_ids.group_id = rec.sale_id.procurement_group_id.id
                else:
                    if rec.chargue_consolidate.operation_type == 'transferencia':
                        rec.chargue_consolidate.state = "patio"

                    picking.check_ids.write({"chargue_consolidate": rec.chargue_consolidate.id})
                    rec.chargue_consolidate.write({
                        "product_id": rec.product_id.id,
                        "check_ids": picking.check_ids[0].id if picking.check_ids else None,
                    })

    def _create_stock_moves(self, picking):
        StockMove = self.env['stock.move'].sudo()

        for line in self:
            template = {
                "product_uom_qty": line.product_uom_qty,
                'name': line.chargue_consolidate.name or '',
                "seed_type_id": line.seed_type_id.id,
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'state': 'draft',
                'company_id': self.env.company.id,
                'price_unit': line.product_id.standard_price,
                'picking_type_id': picking.picking_type_id.id,
                'picking_id': picking.id,
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
                'route_ids': 1 and [
                        (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                'purchase_line_id': line.chargue_consolidate.purchase_id.order_line.filtered(lambda x: x.product_id.id == line.product_id.id).id or False,
                'sale_line_id': line.sale_id.order_line.filtered(lambda x: x.product_id.id == line.product_id.id).id if line.sale_id else False,
            }

            if picking.picking_type_id.code == 'outgoing':
                template.update({
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'location_dest_id': line.partner_id.property_stock_customer.id,
                })
            elif picking.picking_type_id.code == 'incoming':
                template.update({
                    'location_id': line.partner_id.property_stock_supplier.id,
                    'location_dest_id': picking.picking_type_id.default_location_dest_id.id,
                })
            else:
                template.update({
                    'location_id': line.location_src_id.id,
                    'location_dest_id': line.location_dest_id.id,
                })

            StockMove += StockMove \
                .with_context({"chargue_consolidate": self.chargue_consolidate.id}) \
                .create(template)

        return StockMove