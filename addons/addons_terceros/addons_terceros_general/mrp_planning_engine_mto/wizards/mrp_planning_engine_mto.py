# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date


class MrpPlanningEngineMto(models.TransientModel):
    _name = "mrp.planning.engine.mto"
    _description = 'MRP Planning Engine MTO Report'

    sale_id = fields.Many2one("sale.order", 'Sales Order')
    customer_id = fields.Many2one('res.partner', string='Customer', related='sale_id.partner_id')
    user_id = fields.Many2one('res.users', string='Responsible', related='sale_id.user_id')
    line_ids = fields.One2many('mrp.planning.engine.mto.line', 'explosion_id')
    po_line_ids = fields.One2many('mrp.planning.engine.mto.po', 'explosion_id')
    mo_line_ids = fields.One2many('mrp.planning.engine.mto.mo', 'explosion_id')


    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s %s" % ("MRP Planning Engine MTO List: ", record.sale_id.name)
            result.append((record.id, rec_name))
        return result

    def mrp_mto_supply_chain_explosion(self):
        for sale in self.sale_id:
            warehouse = sale.warehouse_id
            mto_origin = sale.name
            # sale items
            for sale_item in sale.order_line:
                self._create_delivery_item(sale_item)
            # MO
            mos = self.env["mrp.production"].search([("mto_origin", "=", mto_origin)])
            for mo in mos.filtered(lambda r: r.state != "cancel"):
                self._create_mo(mo)
            # PO items
            po_items = self.env["purchase.order.line"].search([("mto_origin", "=", mto_origin)])
            for po_item in po_items.filtered(lambda r: r.state != "cancel"):
                self._create_po_item(po_item)
        return {
            'type': 'ir.actions.act_window',
            'name': _('MTO Planning Engine Supply Chain'),
            'res_model': 'mrp.planning.engine.mto',
            'target': 'current',
            'views': [(self.env.ref('mrp_planning_engine_mto.mrp_planning_engine_mto_form2').id, "form")],
            'res_id': self.id,
        }


    def _create_delivery_item(self, sale_item):
        delivery_moves = sale_item.move_ids
        if delivery_moves:
            delivery_move = delivery_moves[0]
            self.env['mrp.planning.engine.mto.line'].create({
                'explosion_id': self.id,
                'product_id': sale_item.product_id.id,
                'qty_planned': sale_item.product_uom_qty,
                'product_uom_id': sale_item.product_uom.id,
                'date_order': sale_item.order_id.date_order,
                'date_planned': sale_item.order_id.commitment_date or sale_item.order_id.expected_date,
                'qty_delivered': sale_item.qty_delivered,
                'date_delivered': delivery_move.date if delivery_move.state == 'done' else False,
                'qty_invoiced': sale_item.qty_invoiced,
                'mto_indicator': sale_item.mto_indicator,
            })

    def _create_po_item(self, po_item):
        self.env['mrp.planning.engine.mto.po'].create({
            'explosion_id': self.id,
            'purchase_id': po_item.order_id.id,
            'partner_id': po_item.order_id.partner_id.id,
            'po_state': po_item.order_id.state,
            'date_order': po_item.order_id.date_order,
            'product_id': po_item.product_id.id,
            'product_qty': po_item.product_uom_qty,
            'product_uom_id': po_item.product_uom.id,
            'date_planned': po_item.date_planned,
            'poitem_qty_received': po_item.qty_received,
        })

    def _create_mo(self, mo):
        self.env['mrp.planning.engine.mto.mo'].create({
            'explosion_id': self.id,
            'production_id': mo.id,
            'mo_state': mo.state,
            'product_id': mo.product_id.id,
            'product_qty': mo.product_qty,
            'qty_producing': mo.qty_producing,
            'product_uom_id': mo.product_uom_id.id,
            'date_planned_start_pivot': mo.date_planned_start_pivot,
            'date_planned_finished_pivot': mo.date_planned_finished_pivot,
            'explosion_id': self.id,
        })


class MrpPlanningEngineMtoLine(models.TransientModel):
    _name = "mrp.planning.engine.mto.line"
    _description = 'MRP Planning Engine MTO Line Report'
    _order = "date_planned"

    explosion_id = fields.Many2one('mrp.planning.engine.mto')
    product_id = fields.Many2one('product.product')
    qty_planned = fields.Float('Requested Qty', digits='Product Unit of Measure')
    product_uom_id = fields.Many2one('uom.uom', 'UoM')
    date_order = fields.Datetime('Order Date')
    date_planned = fields.Datetime('Planned Delivery Date')
    qty_delivered = fields.Float('Delivered Qty', digits='Product Unit of Measure')
    qty_invoiced = fields.Float('Invoiced Qty', digits='Product Unit of Measure')
    mto_indicator = fields.Boolean('MTO')
    date_delivered = fields.Datetime('Delivery Date')



class MrpPlanningEngineMtoPurchase(models.TransientModel):
    _name = "mrp.planning.engine.mto.po"
    _description = 'MRP Planning Engine MTO Subline Purchase Report'
    _order = "date_order"

    explosion_id = fields.Many2one('mrp.planning.engine.mto')
    purchase_id = fields.Many2one('purchase.order')
    partner_id = fields.Many2one('res.partner', 'Supplier')
    po_state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked')], string='Status')
    date_order = fields.Datetime('Order Date')
    product_id = fields.Many2one('product.product')
    product_qty = fields.Float('Requested Qty', digits='Product Unit of Measure')
    product_uom_id = fields.Many2one('uom.uom', 'UoM')
    date_planned = fields.Datetime('Planned Delivery Date')
    poitem_qty_received = fields.Float('Received Qty', digits='Product Unit of Measure')


class MrpPlanningEngineMtoProduction(models.TransientModel):
    _name = "mrp.planning.engine.mto.mo"
    _description = 'MRP Planning Engine MTO Subline Produciton Report'
    _order = "date_planned_start_pivot"

    explosion_id = fields.Many2one('mrp.planning.engine.mto')
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order')
    mo_state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done')], string='Status')
    product_id = fields.Many2one('product.product')
    product_qty = fields.Float('Requested Qty', digits='Product Unit of Measure')
    product_uom_id = fields.Many2one('uom.uom', 'UoM')
    qty_producing = fields.Float('Produced Qty', digits='Product Unit of Measure')
    date_planned_start_pivot = fields.Datetime('Planned Start Pivot Date')
    date_planned_finished_pivot = fields.Datetime('Planned End Pivot Date')
