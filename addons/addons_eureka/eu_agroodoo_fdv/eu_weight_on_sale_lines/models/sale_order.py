from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit="sale.order"


    total_order_weight=fields.Float(string="Peso Total",store=True, compute="_compute_t_weight")
    weight_uom=fields.Char(compute="_compute_t_weight")

    @api.depends('order_line','order_line.weight','order_line.product_uom_qty','__last_update','order_line.product_id')
    def _compute_t_weight(self):
        for rec in self:
            weight=0
            weight_uom=[]
            rec.weight_uom = ''
            for line in rec.order_line:
                if line.weight and line.product_id.weight_uom_name :
                    weight+=line.weight_total
                    weight_uom.append(line.product_id.weight_uom_name)
            rec.total_order_weight=weight
            if len(weight_uom)>0:
                rec.weight_uom=','.join(list(set(weight_uom)))



class SaleOrderLine(models.Model):
    _inherit="sale.order.line"

    weight=fields.Float(related="product_id.weight")
    weight_uom=fields.Char(related="product_id.weight_uom_name",store=True)

    weight_total=fields.Float(compute="_compute_t_weight",store=True,string="Peso total")


    @api.depends('weight','product_uom_qty','qty_delivered','__last_update')
    def _compute_t_weight(self):
        for rec in self:
            if rec.weight and rec.product_uom:
                if rec.product_uom.uom_type==False:
                    raise UserError("Configure la unidad de medida")
                # if rec.product_uom_id.uom_type=="reference":
                #     rec.weight_total=rec.weight*rec.quantity
                # elif rec.product_uom_id.uom_type=="smaller":
                #     rec.weight_total=rec.weight*rec.quantity / (rec.product_uom_id.ratio if rec.product_uom_id.ratio>0 else 1)
                # else:
                    
                rec.weight_total=rec.weight*rec.product_uom._compute_quantity(rec.product_qty,rec.product_id.uom_id )
            else:
                rec.weight_total=0



    